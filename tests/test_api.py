from datetime import datetime

import pytest
from fastapi.testclient import TestClient

from app.models import Analytics, Call


def test_health_check(client):
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_root_endpoint(client):
    """Test root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    assert "Sales Call Analytics API" in response.json()["message"]


def test_get_calls_empty(client):
    """Test get calls with empty database."""
    response = client.get("/api/v1/calls")
    assert response.status_code == 200
    assert response.json() == []


def test_get_calls_with_data(client, sample_call):
    """Test get calls with sample data."""
    response = client.get("/api/v1/calls")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["call_id"] == sample_call.call_id
    assert data[0]["agent_id"] == sample_call.agent_id


def test_get_calls_with_filters(client, db_session):
    """Test get calls with various filters."""
    # Create multiple test calls
    calls_data = [
        {
            "call_id": "CALL_001",
            "agent_id": "AGENT_1",
            "customer_id": "CUST_001",
            "language": "en",
            "start_time": datetime(2023, 7, 1, 10, 0, 0),
            "duration_seconds": 1800,
            "transcript": "Test transcript 1",
            "customer_sentiment_score": 0.8,
        },
        {
            "call_id": "CALL_002",
            "agent_id": "AGENT_2",
            "customer_id": "CUST_002",
            "language": "en",
            "start_time": datetime(2023, 7, 2, 10, 0, 0),
            "duration_seconds": 2400,
            "transcript": "Test transcript 2",
            "customer_sentiment_score": -0.2,
        },
    ]

    for call_data in calls_data:
        call = Call(**call_data)
        db_session.add(call)
    db_session.commit()

    # Test filter by agent_id
    response = client.get("/api/v1/calls?agent_id=AGENT_1")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["agent_id"] == "AGENT_1"

    # Test filter by sentiment
    response = client.get("/api/v1/calls?min_sentiment=0.5")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["customer_sentiment_score"] >= 0.5


def test_get_call_detail(client, sample_call):
    """Test get call detail endpoint."""
    response = client.get(f"/api/v1/calls/{sample_call.call_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["call_id"] == sample_call.call_id
    assert data["transcript"] == sample_call.transcript


def test_get_call_detail_not_found(client):
    """Test get call detail for non-existent call."""
    response = client.get("/api/v1/calls/NON_EXISTENT")
    assert response.status_code == 404
    assert "Call not found" in response.json()["detail"]


def test_get_call_recommendations(client, db_session):
    """Test get call recommendations endpoint."""
    # Create a call with embedding
    call_data = {
        "call_id": "CALL_WITH_EMBEDDING",
        "agent_id": "AGENT_1",
        "customer_id": "CUST_001",
        "language": "en",
        "start_time": datetime(2023, 7, 1, 10, 0, 0),
        "duration_seconds": 1800,
        "transcript": "Agent: Hello, how can I help?\nCustomer: I need support.",
        "customer_sentiment_score": 0.5,
        "agent_talk_ratio": 0.6,
    }

    call = Call(**call_data)
    # Set embedding using the proper method
    call.set_embedding([0.1, 0.2, 0.3, 0.4, 0.5])
    db_session.add(call)
    db_session.commit()

    response = client.get(f"/api/v1/calls/{call.call_id}/recommendations")
    assert response.status_code == 200
    data = response.json()
    assert "similar_calls" in data
    assert "coaching_nudges" in data
    assert len(data["coaching_nudges"]) <= 3


def test_get_call_recommendations_no_embedding(client, sample_call):
    """Test get call recommendations for call without embedding."""
    # Remove embedding from sample call
    sample_call.embedding = None

    response = client.get(f"/api/v1/calls/{sample_call.call_id}/recommendations")
    assert response.status_code == 400
    assert "Call embedding not available" in response.json()["detail"]


def test_get_agent_analytics_empty(client):
    """Test agent analytics with empty database."""
    response = client.get("/api/v1/analytics/agents")
    assert response.status_code == 200
    data = response.json()
    assert data["agents"] == []


def test_get_agent_analytics_with_data(client, db_session):
    """Test agent analytics with sample data."""
    # Create analytics data
    analytics = Analytics(
        agent_id="AGENT_1", avg_sentiment=0.75, avg_talk_ratio=0.65, total_calls=5
    )
    db_session.add(analytics)
    db_session.commit()

    response = client.get("/api/v1/analytics/agents")
    assert response.status_code == 200
    data = response.json()
    assert len(data["agents"]) == 1
    assert data["agents"][0]["agent_id"] == "AGENT_1"
    assert data["agents"][0]["avg_sentiment"] == 0.75
    assert data["agents"][0]["total_calls"] == 5


def test_pagination(client, db_session):
    """Test pagination parameters."""
    # Create multiple calls
    for i in range(25):
        call = Call(
            call_id=f"CALL_{i:03d}",
            agent_id=f"AGENT_{i % 3}",
            customer_id=f"CUST_{i:03d}",
            language="en",
            start_time=datetime(2023, 7, 1, 10, 0, 0),
            duration_seconds=1800,
            transcript=f"Test transcript {i}",
        )
        db_session.add(call)
    db_session.commit()

    # Test limit
    response = client.get("/api/v1/calls?limit=10")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 10

    # Test offset
    response = client.get("/api/v1/calls?limit=10&offset=10")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 10


def test_invalid_parameters(client):
    """Test invalid query parameters."""
    # Test invalid limit
    response = client.get("/api/v1/calls?limit=0")
    assert response.status_code == 422  # Validation error

    # Test invalid sentiment range
    response = client.get("/api/v1/calls?min_sentiment=2.0")
    assert response.status_code == 422  # Validation error
