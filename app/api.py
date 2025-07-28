from fastapi import APIRouter, Depends, HTTPException, status, Query, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from typing import List, Optional
from datetime import datetime
import asyncio
import json
import random
import logging

from app.database import get_db
from app.models import Call, Analytics
from app.schemas import (
    CallResponse, CallDetail, CallsQuery, RecommendationsResponse,
    AnalyticsResponse, AgentAnalytics, SimilarCall, CoachingNudge,
    ErrorResponse, SentimentUpdate
)
from app.ai_insights import AIInsightModule

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1")
ai_module = AIInsightModule()

@router.get("/calls", response_model=List[CallResponse])
async def get_calls(
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    agent_id: Optional[str] = Query(None),
    from_date: Optional[datetime] = Query(None),
    to_date: Optional[datetime] = Query(None),
    min_sentiment: Optional[float] = Query(None, ge=-1, le=1),
    max_sentiment: Optional[float] = Query(None, ge=-1, le=1),
    db: Session = Depends(get_db)
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
            detail="Error fetching calls"
        )

@router.get("/calls/{call_id}", response_model=CallDetail)
async def get_call_detail(call_id: str, db: Session = Depends(get_db)):
    """Get complete details of one call."""
    try:
        call = db.query(Call).filter(Call.call_id == call_id).first()
        if not call:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Call not found"
            )
        return call
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching call detail: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error fetching call detail"
        )

@router.get("/calls/{call_id}/recommendations", response_model=RecommendationsResponse)
async def get_call_recommendations(call_id: str, db: Session = Depends(get_db)):
    """Get similar calls and coaching nudges for a specific call."""
    try:
        # Get the target call
        target_call = db.query(Call).filter(Call.call_id == call_id).first()
        if not target_call:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Call not found"
            )
        
        if not target_call.embedding:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Call embedding not available"
            )
        
        # Get other calls with embeddings (excluding the target call)
        other_calls = db.query(Call).filter(
            and_(Call.call_id != call_id, Call.embedding.isnot(None))
        ).limit(50).all()  # Limit for performance
        
        # Prepare data for similarity calculation
        call_embeddings = [
            {
                'call_id': call.call_id,
                'agent_id': call.agent_id,
                'embedding': call.embedding,
                'transcript': call.transcript
            }
            for call in other_calls
        ]
        
        # Find similar calls
        similar_calls_data = ai_module.find_similar_calls(
            target_call.embedding, call_embeddings, top_k=5
        )
        
        similar_calls = [
            SimilarCall(**call_data) for call_data in similar_calls_data
        ]
        
        # Generate coaching nudges
        coaching_messages = ai_module.generate_coaching_nudges(
            target_call.transcript,
            target_call.customer_sentiment_score or 0.0,
            target_call.agent_talk_ratio or 0.5
        )
        
        coaching_nudges = [
            CoachingNudge(message=message) for message in coaching_messages
        ]
        
        return RecommendationsResponse(
            similar_calls=similar_calls,
            coaching_nudges=coaching_nudges
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating recommendations: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error generating recommendations"
        )

@router.get("/analytics/agents", response_model=AnalyticsResponse)
async def get_agent_analytics(db: Session = Depends(get_db)):
    """Get agent leaderboard with analytics."""
    try:
        # Query agent analytics from the analytics table
        analytics = db.query(Analytics).all()
        
        # If analytics table is empty, calculate on the fly
        if not analytics:
            agent_stats = db.query(
                Call.agent_id,
                func.avg(Call.customer_sentiment_score).label('avg_sentiment'),
                func.avg(Call.agent_talk_ratio).label('avg_talk_ratio'),
                func.count(Call.id).label('total_calls')
            ).group_by(Call.agent_id).all()
            
            agent_analytics = [
                AgentAnalytics(
                    agent_id=stat.agent_id,
                    avg_sentiment=float(stat.avg_sentiment) if stat.avg_sentiment else None,
                    avg_talk_ratio=float(stat.avg_talk_ratio) if stat.avg_talk_ratio else None,
                    total_calls=stat.total_calls
                )
                for stat in agent_stats
            ]
        else:
            agent_analytics = [
                AgentAnalytics(
                    agent_id=analytic.agent_id,
                    avg_sentiment=analytic.avg_sentiment,
                    avg_talk_ratio=analytic.avg_talk_ratio,
                    total_calls=analytic.total_calls
                )
                for analytic in analytics
            ]
        
        return AnalyticsResponse(agents=agent_analytics)
        
    except Exception as e:
        logger.error(f"Error fetching agent analytics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error fetching agent analytics"
        )

# WebSocket endpoint for real-time sentiment updates (bonus feature)
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
                timestamp=datetime.utcnow()
            )
            
            await websocket.send_text(sentiment_update.model_dump_json())
            await asyncio.sleep(2)  # Send update every 2 seconds
            
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for call {call_id}")
    except Exception as e:
        logger.error(f"WebSocket error for call {call_id}: {e}")
        await websocket.close()
