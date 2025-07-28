import pytest
from app.ai_insights import AIInsightModule

@pytest.fixture
def ai_module():
    return AIInsightModule()

def test_generate_embedding(ai_module):
    """Test embedding generation."""
    text = "This is a test sentence for embedding generation."
    embedding = ai_module.generate_embedding(text)
    
    assert isinstance(embedding, list)
    assert len(embedding) > 0
    assert all(isinstance(x, float) for x in embedding)

def test_analyze_sentiment(ai_module):
    """Test sentiment analysis."""
    positive_text = "I'm very happy with this product! It's amazing!"
    negative_text = "This is terrible and I hate it."
    neutral_text = "The weather is okay today."
    
    positive_score = ai_module.analyze_sentiment(positive_text)
    negative_score = ai_module.analyze_sentiment(negative_text)
    neutral_score = ai_module.analyze_sentiment(neutral_text)
    
    assert -1.0 <= positive_score <= 1.0
    assert -1.0 <= negative_score <= 1.0
    assert -1.0 <= neutral_score <= 1.0
    
    # Generally positive should be > negative
    assert positive_score > negative_score

def test_calculate_agent_talk_ratio(ai_module):
    """Test agent talk ratio calculation."""
    transcript = """Agent: Hello, how can I help you today?
Customer: I need help with my account.
Agent: I'd be happy to help you with that. Can you tell me more about the issue?
Customer: Sure."""
    
    talk_ratio = ai_module.calculate_agent_talk_ratio(transcript)
    
    assert 0.0 <= talk_ratio <= 1.0
    # Agent spoke more in this example
    assert talk_ratio > 0.5

def test_find_similar_calls(ai_module):
    """Test finding similar calls."""
    target_embedding = [0.1, 0.2, 0.3, 0.4, 0.5]
    
    call_embeddings = [
        {
            'call_id': 'CALL_001',
            'agent_id': 'AGENT_1',
            'embedding': [0.1, 0.2, 0.3, 0.4, 0.5],  # Identical
            'transcript': 'Test transcript 1'
        },
        {
            'call_id': 'CALL_002',
            'agent_id': 'AGENT_2',
            'embedding': [0.9, 0.8, 0.7, 0.6, 0.5],  # Different
            'transcript': 'Test transcript 2'
        },
        {
            'call_id': 'CALL_003',
            'agent_id': 'AGENT_3',
            'embedding': [0.15, 0.25, 0.35, 0.45, 0.55],  # Similar
            'transcript': 'Test transcript 3'
        }
    ]
    
    similar_calls = ai_module.find_similar_calls(target_embedding, call_embeddings, top_k=2)
    
    assert len(similar_calls) == 2
    assert similar_calls[0]['call_id'] == 'CALL_001'  # Most similar should be first
    assert similar_calls[0]['similarity_score'] > similar_calls[1]['similarity_score']

def test_generate_coaching_nudges(ai_module):
    """Test coaching nudge generation."""
    transcript = "Agent: Hello. Customer: I'm not happy."
    sentiment_score = -0.5
    talk_ratio = 0.3
    
    nudges = ai_module.generate_coaching_nudges(transcript, sentiment_score, talk_ratio)
    
    assert isinstance(nudges, list)
    assert len(nudges) <= 3
    assert all(isinstance(nudge, str) for nudge in nudges)
    assert all(len(nudge) <= 40 for nudge in nudges)

def test_rule_based_nudges(ai_module):
    """Test rule-based nudge generation."""
    # Test low sentiment
    nudges = ai_module._generate_rule_based_nudges(-0.5, 0.5)
    assert any("empathetically" in nudge.lower() or "positive" in nudge.lower() for nudge in nudges)
    
    # Test high talk ratio
    nudges = ai_module._generate_rule_based_nudges(0.0, 0.8)
    assert any("listen" in nudge.lower() for nudge in nudges)
    
    # Test low talk ratio
    nudges = ai_module._generate_rule_based_nudges(0.0, 0.3)
    assert any("initiative" in nudge.lower() for nudge in nudges)

def test_empty_inputs(ai_module):
    """Test handling of empty inputs."""
    # Empty text
    embedding = ai_module.generate_embedding("")
    assert isinstance(embedding, list)
    
    sentiment = ai_module.analyze_sentiment("")
    assert -1.0 <= sentiment <= 1.0
    
    # Empty call embeddings
    similar_calls = ai_module.find_similar_calls([0.1, 0.2], [], top_k=5)
    assert similar_calls == []

def test_error_handling(ai_module, monkeypatch):
    """Test error handling in AI module."""
    # Mock embedding model to raise exception
    def mock_encode(text):
        raise Exception("Test error")
    
    monkeypatch.setattr(ai_module.embedding_model, 'encode', mock_encode)
    
    embedding = ai_module.generate_embedding("test")
    assert embedding == []  # Should return empty list on error
