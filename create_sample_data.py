#!/usr/bin/env python3
"""
Create sample data for testing the API.
Run this script to populate the database with test data.
"""

from datetime import datetime, timedelta
import random
import uuid
from faker import Faker

from app.database import SessionLocal, engine
from app.models import Call, Analytics, Base

# Create tables if they don't exist
Base.metadata.create_all(bind=engine)

fake = Faker()

def create_sample_calls(num_calls=20):
    """Create sample call data"""
    db = SessionLocal()
    
    try:
        agents = ['agent_001', 'agent_002', 'agent_003', 'agent_004', 'agent_005']
        sample_transcripts = [
            "Hello, thank you for calling. How can I help you today? I understand you're interested in our premium service package. Let me explain the benefits...",
            "Good morning! I see you've been having some issues with your account. Let me look into that for you right away.",
            "Thanks for reaching out. I noticed you're looking to upgrade your current plan. Here are some options that might work for you...",
            "Hi there! I'm calling to follow up on your recent inquiry about our new product line. Do you have a few minutes to discuss?",
            "Hello! I understand you have some questions about our billing. I'm here to help clarify everything for you.",
            "Good afternoon! Thank you for your patience. I've reviewed your case and have some great solutions to propose.",
            "Hi! I see you're interested in our enterprise solution. Let me walk you through the features that would benefit your company.",
            "Hello! I'm calling regarding your recent support ticket. I have some updates and solutions for you.",
            "Good morning! Thanks for choosing our service. I wanted to personally ensure you're completely satisfied with your experience.",
            "Hi there! I noticed you've been exploring our website. I'd love to help answer any questions you might have."
        ]
        
        for i in range(num_calls):
            # Generate realistic call data
            agent_id = random.choice(agents)
            start_time = fake.date_time_between(start_date='-30d', end_date='now')
            duration = random.randint(180, 1800)  # 3-30 minutes
            transcript = random.choice(sample_transcripts)
            
            # Generate some realistic AI insights
            sentiment_score = random.uniform(-0.3, 0.8)  # Slightly positive bias
            talk_ratio = random.uniform(0.3, 0.7)  # Agent talks 30-70% of time
            
            # Generate a simple embedding (normally this would come from sentence transformers)
            embedding = [random.uniform(-1, 1) for _ in range(384)]  # 384-dim embedding
            
            call = Call(
                call_id=f"call_{i+1:04d}",
                agent_id=agent_id,
                customer_id=f"customer_{random.randint(1, 100):03d}",
                language="en",
                start_time=start_time,
                duration_seconds=duration,
                transcript=transcript,
                agent_talk_ratio=talk_ratio,
                customer_sentiment_score=sentiment_score,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            # Set embedding using the helper method
            call.set_embedding(embedding)
            
            db.add(call)
        
        db.commit()
        print(f"✅ Created {num_calls} sample calls")
        
        # Create some sample analytics
        for agent_id in agents:
            agent_calls = db.query(Call).filter(Call.agent_id == agent_id).all()
            if agent_calls:
                avg_sentiment = sum(c.customer_sentiment_score for c in agent_calls) / len(agent_calls)
                avg_talk_ratio = sum(c.agent_talk_ratio for c in agent_calls) / len(agent_calls)
                
                analytics = Analytics(
                    agent_id=agent_id,
                    avg_sentiment=avg_sentiment,
                    avg_talk_ratio=avg_talk_ratio,
                    total_calls=len(agent_calls),
                    last_updated=datetime.utcnow()
                )
                db.add(analytics)
        
        db.commit()
        print(f"✅ Created analytics for {len(agents)} agents")
        
    except Exception as e:
        print(f"❌ Error creating sample data: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("🔧 Creating sample data for API testing...")
    create_sample_calls(20)
    print("🎉 Sample data creation complete!")
