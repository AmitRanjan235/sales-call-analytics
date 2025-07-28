import os
import tempfile
from datetime import datetime

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from app.main import app
from app.models import Analytics, Call

# Use SQLite for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session")
def test_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session(test_db):
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    yield session
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture
def sample_call_data():
    return {
        "call_id": "TEST_CALL_001",
        "agent_id": "AGENT_1",
        "customer_id": "CUST_001",
        "language": "en",
        "start_time": datetime(2023, 7, 1, 10, 0, 0),
        "duration_seconds": 1800,
        "transcript": "Agent: Hello, how can I help you today?\nCustomer: I'm interested in your product.",
        "agent_talk_ratio": 0.6,
        "customer_sentiment_score": 0.8,
        "embedding": [0.1, 0.2, 0.3, 0.4, 0.5],
    }


@pytest.fixture
def sample_call(db_session, sample_call_data):
    # Extract embedding to handle separately
    embedding_data = sample_call_data.pop("embedding", None)
    call = Call(**sample_call_data)

    # Set embedding using the proper method
    if embedding_data:
        call.set_embedding(embedding_data)

    db_session.add(call)
    db_session.commit()
    db_session.refresh(call)
    return call
