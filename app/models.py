import json
import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, Float, Integer, String, Text
from sqlalchemy.ext.hybrid import hybrid_property

from app.database import Base


class Call(Base):
    __tablename__ = "calls"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
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
    embedding = Column(Text)  # Store as JSON string for SQLite compatibility

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    @hybrid_property
    def duration_minutes(self):
        return self.duration_seconds / 60.0

    @property
    def embedding_list(self):
        """Convert embedding JSON string to list of floats."""
        if self.embedding:
            try:
                return json.loads(self.embedding)
            except (json.JSONDecodeError, TypeError):
                return None
        return None

    def set_embedding(self, embedding_list):
        """Set embedding from list of floats."""
        if embedding_list:
            self.embedding = json.dumps(embedding_list)
        else:
            self.embedding = None


class Analytics(Base):
    __tablename__ = "analytics"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    agent_id = Column(String, nullable=False, unique=True)
    avg_sentiment = Column(Float)
    avg_talk_ratio = Column(Float)
    total_calls = Column(Integer, default=0)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
