import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from app.models import Analytics, Call


class TestDatabase:
    """Test database functionality."""

    def test_database_connection(self, db_session):
        """Test database connection works."""
        # Should be able to query without errors
        from sqlalchemy import text

        result = db_session.execute(text("SELECT 1")).scalar()
        assert result == 1

    def test_call_model_creation(self, db_session, sample_call_data):
        """Test Call model creation and retrieval."""
        # Remove embedding for direct model creation
        call_data = sample_call_data.copy()
        call_data.pop("embedding", None)

        call = Call(**call_data)
        db_session.add(call)
        db_session.commit()
        db_session.refresh(call)

        # Verify the call was created
        assert call.id is not None
        assert call.call_id == call_data["call_id"]
        assert call.agent_id == call_data["agent_id"]

    def test_analytics_model_creation(self, db_session):
        """Test Analytics model creation and retrieval."""
        analytics = Analytics(
            agent_id="TEST_AGENT",
            avg_sentiment=0.75,
            avg_talk_ratio=0.65,
            total_calls=10,
        )
        db_session.add(analytics)
        db_session.commit()
        db_session.refresh(analytics)

        # Verify the analytics was created
        assert analytics.id is not None
        assert analytics.agent_id == "TEST_AGENT"
        assert analytics.avg_sentiment == 0.75
        assert analytics.total_calls == 10

    def test_call_embedding_methods(self, db_session, sample_call_data):
        """Test Call model embedding methods."""
        call_data = sample_call_data.copy()
        call_data.pop("embedding", None)

        call = Call(**call_data)

        # Test setting embedding
        test_embedding = [0.1, 0.2, 0.3]
        call.set_embedding(test_embedding)

        db_session.add(call)
        db_session.commit()
        db_session.refresh(call)

        # Test getting embedding
        retrieved_embedding = call.embedding_list
        assert retrieved_embedding == test_embedding

    def test_call_duration_minutes_property(self, db_session, sample_call_data):
        """Test Call model duration_minutes property."""
        call_data = sample_call_data.copy()
        call_data.pop("embedding", None)
        call_data["duration_seconds"] = 3600  # 1 hour

        call = Call(**call_data)
        db_session.add(call)
        db_session.commit()

        assert call.duration_minutes == 60.0
