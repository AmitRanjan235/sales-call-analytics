from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class CallBase(BaseModel):
    call_id: str
    agent_id: str
    customer_id: str
    language: str = "en"
    start_time: datetime
    duration_seconds: int
    transcript: str


class CallCreate(CallBase):
    pass


class CallResponse(CallBase):
    id: str
    agent_talk_ratio: Optional[float] = None
    customer_sentiment_score: Optional[float] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CallDetail(CallResponse):
    embedding: Optional[List[float]] = None


class CallsQuery(BaseModel):
    limit: int = Field(default=10, ge=1, le=100)
    offset: int = Field(default=0, ge=0)
    agent_id: Optional[str] = None
    from_date: Optional[datetime] = None
    to_date: Optional[datetime] = None
    min_sentiment: Optional[float] = Field(default=None, ge=-1, le=1)
    max_sentiment: Optional[float] = Field(default=None, ge=-1, le=1)


class SimilarCall(BaseModel):
    call_id: str
    agent_id: str
    similarity_score: float
    transcript_preview: str


class CoachingNudge(BaseModel):
    message: str = Field(max_length=40)


class RecommendationsResponse(BaseModel):
    similar_calls: List[SimilarCall]
    coaching_nudges: List[CoachingNudge]


class AgentAnalytics(BaseModel):
    agent_id: str
    avg_sentiment: Optional[float]
    avg_talk_ratio: Optional[float]
    total_calls: int

    model_config = ConfigDict(from_attributes=True)


class AnalyticsResponse(BaseModel):
    agents: List[AgentAnalytics]


class ErrorResponse(BaseModel):
    detail: str
    error_code: Optional[str] = None


class SentimentUpdate(BaseModel):
    call_id: str
    sentiment_score: float
    timestamp: datetime
