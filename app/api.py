import asyncio
import json
import logging
import random
from datetime import datetime
from typing import List, Optional

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    WebSocket,
    WebSocketDisconnect,
    status,
)
from sqlalchemy import and_, func, or_
from sqlalchemy.orm import Session

from app.ai_insights import AIInsightModule
from app.database import get_db
from app.models import Analytics, Call
from app.schemas import (
    AgentAnalytics,
    AnalyticsResponse,
    CallDetail,
    CallResponse,
    CallsQuery,
    CoachingNudge,
    ErrorResponse,
    RecommendationsResponse,
    SentimentUpdate,
    SimilarCall,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1")
ai_module = AIInsightModule()


@router.get("/health")
async def health_check():
    """Health check endpoint for monitoring."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "sales-call-analytics",
        "version": "1.0.0",
    }


@router.get("/calls", response_model=List[CallResponse])
async def get_calls(
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    agent_id: Optional[str] = Query(None),
    from_date: Optional[datetime] = Query(None),
    to_date: Optional[datetime] = Query(None),
    min_sentiment: Optional[float] = Query(None, ge=-1, le=1),
    max_sentiment: Optional[float] = Query(None, ge=-1, le=1),
    db: Session = Depends(get_db),
):
    """Get calls with optional filtering."""
    try:
        query = db.query(Call)

        # Apply filters
        filters = []
        if agent_id:
            filters.append(Call.agent_id == agent_id)
        if from_date:
            filters.append(Call.start_time >= from_date)
        if to_date:
            filters.append(Call.start_time <= to_date)
        if min_sentiment is not None:
            filters.append(Call.customer_sentiment_score >= min_sentiment)
        if max_sentiment is not None:
            filters.append(Call.customer_sentiment_score <= max_sentiment)

        if filters:
            query = query.filter(and_(*filters))

        calls = query.offset(offset).limit(limit).all()
        return calls

    except Exception as e:
        logger.error(f"Error fetching calls: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error fetching calls",
        )


@router.get("/calls/{call_id}", response_model=CallDetail)
async def get_call_detail(call_id: str, db: Session = Depends(get_db)):
    """Get complete details of one call."""
    try:
        call = db.query(Call).filter(Call.call_id == call_id).first()
        if not call:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Call not found"
            )

        # Create response with embedding as list
        call_detail = CallDetail(
            id=str(getattr(call, "id", "")),
            call_id=str(getattr(call, "call_id", "")),
            agent_id=str(getattr(call, "agent_id", "")),
            customer_id=str(getattr(call, "customer_id", "")),
            language=str(getattr(call, "language", "")),
            start_time=getattr(call, "start_time", datetime.utcnow()),
            duration_seconds=int(getattr(call, "duration_seconds", 0)),
            transcript=str(getattr(call, "transcript", "")),
            agent_talk_ratio=float(getattr(call, "agent_talk_ratio", 0.0))
            if getattr(call, "agent_talk_ratio", None) is not None
            else None,
            customer_sentiment_score=float(
                getattr(call, "customer_sentiment_score", 0.0)
            )
            if getattr(call, "customer_sentiment_score", None) is not None
            else None,
            created_at=getattr(call, "created_at", datetime.utcnow()),
            updated_at=getattr(call, "updated_at", datetime.utcnow()),
            embedding=call.embedding_list,
        )
        return call_detail

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching call detail: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error fetching call detail",
        )


@router.get("/calls/{call_id}/recommendations", response_model=RecommendationsResponse)
async def get_call_recommendations(call_id: str, db: Session = Depends(get_db)):
    """Get similar calls and coaching nudges for a specific call."""
    try:
        # Get the target call
        target_call = db.query(Call).filter(Call.call_id == call_id).first()
        if not target_call:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Call not found"
            )

        target_embedding = target_call.embedding_list
        if not target_embedding:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Call embedding not available",
            )

        # Get other calls with embeddings (excluding the target call)
        other_calls = (
            db.query(Call)
            .filter(and_(Call.call_id != call_id, Call.embedding.isnot(None)))
            .limit(50)
            .all()
        )  # Limit for performance

        # Prepare data for similarity calculation
        call_embeddings = []
        for call in other_calls:
            embedding = call.embedding_list
            if embedding:  # Only include calls with valid embeddings
                call_embeddings.append(
                    {
                        "call_id": call.call_id,
                        "agent_id": call.agent_id,
                        "embedding": embedding,
                        "transcript": call.transcript,
                    }
                )

        # Find similar calls
        similar_calls_data = ai_module.find_similar_calls(
            target_embedding, call_embeddings, top_k=5
        )

        similar_calls = [SimilarCall(**call_data) for call_data in similar_calls_data]

        # Generate coaching nudges
        coaching_messages = ai_module.generate_coaching_nudges(
            str(getattr(target_call, "transcript", "")),
            float(getattr(target_call, "customer_sentiment_score", 0.0) or 0.0),
            float(getattr(target_call, "agent_talk_ratio", 0.5) or 0.5),
        )

        coaching_nudges = [
            CoachingNudge(message=message) for message in coaching_messages
        ]

        return RecommendationsResponse(
            similar_calls=similar_calls, coaching_nudges=coaching_nudges
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating recommendations: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error generating recommendations",
        )


@router.get("/analytics/agents", response_model=AnalyticsResponse)
async def get_agent_analytics(db: Session = Depends(get_db)):
    """Get agent leaderboard with analytics."""
    try:
        # Query agent analytics from the analytics table
        analytics = db.query(Analytics).all()

        # If analytics table is empty, calculate on the fly
        if not analytics:
            agent_stats = (
                db.query(
                    Call.agent_id,
                    func.avg(Call.customer_sentiment_score).label("avg_sentiment"),
                    func.avg(Call.agent_talk_ratio).label("avg_talk_ratio"),
                    func.count(Call.id).label("total_calls"),
                )
                .group_by(Call.agent_id)
                .all()
            )

            agent_analytics = [
                AgentAnalytics(
                    agent_id=stat.agent_id,
                    avg_sentiment=float(stat.avg_sentiment)
                    if stat.avg_sentiment
                    else None,
                    avg_talk_ratio=float(stat.avg_talk_ratio)
                    if stat.avg_talk_ratio
                    else None,
                    total_calls=stat.total_calls,
                )
                for stat in agent_stats
            ]
        else:
            agent_analytics = [
                AgentAnalytics(
                    agent_id=str(getattr(analytic, "agent_id", "")),
                    avg_sentiment=getattr(analytic, "avg_sentiment", None),
                    avg_talk_ratio=getattr(analytic, "avg_talk_ratio", None),
                    total_calls=int(getattr(analytic, "total_calls", 0)),
                )
                for analytic in analytics
            ]

        return AnalyticsResponse(agents=agent_analytics)

    except Exception as e:
        logger.error(f"Error fetching agent analytics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error fetching agent analytics",
        )


# WebSocket endpoint for real-time sentiment updates
@router.websocket("/ws/sentiment/{call_id}")
async def websocket_sentiment_updates(websocket: WebSocket, call_id: str):
    """Stream real-time sentiment updates for a call."""
    await websocket.accept()

    try:
        # Simulate real-time sentiment updates
        while True:
            # Generate random sentiment update (simulate real-time analysis)
            sentiment_update = SentimentUpdate(
                call_id=call_id,
                sentiment_score=random.uniform(-1.0, 1.0),
                timestamp=datetime.utcnow(),
            )

            await websocket.send_text(sentiment_update.model_dump_json())
            await asyncio.sleep(2)  # Send update every 2 seconds

    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for call {call_id}")
    except Exception as e:
        logger.error(f"WebSocket error for call {call_id}: {e}")
        await websocket.close()
