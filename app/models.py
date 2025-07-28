from sqlalchemy import Column, Integer, String, DateTime, Float, Text, Index, func
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.ext.hybrid import hybrid_property
from app.database import Base
import uuid
from datetime import datetime


class Call(Base):
    __tablename__ = "calls"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    call_id = Column(String, unique=True, nullable=False, index=True)
    agent_id = Column(String, nullable=False, index=True)
    customer_id = Column(String, nullable=False)
    language = Column(String, nullable=False, default="en")
    start_time = Column(DateTime, nullable=False, index=True)
    duration_seconds = Column(Integer, nullable=False)
    transcript = Column(Text, nullable=False)
    
    # AI insights
    agent_talk_ratio = Column(Float)
    customer_sentiment_score = Column(Float)
    embedding = Column(ARRAY(Float))
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Full-text search index using tsvector + GIN
    # GIN index is chosen for full-text search as it provides faster search performance
    # for complex text queries compared to GiST, especially for large datasets
    __table_args__ = (
        Index('ix_calls_transcript_fts', 
              func.to_tsvector('english', transcript), 
              postgresql_using='gin'),
    )

    @hybrid_property
    def duration_minutes(self):
        return self.duration_seconds / 60.0


class Analytics(Base):
    __tablename__ = "analytics"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    agent_id = Column(String, nullable=False, unique=True)
    avg_sentiment = Column(Float)
    avg_talk_ratio = Column(Float)
    total_calls = Column(Integer, default=0)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
