import asyncio
import json
import logging
import os
import random
import sys
from datetime import datetime, timedelta
from typing import Any, Dict, List

import aiohttp
from faker import Faker

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

from sqlalchemy.orm import Session

from app.ai_insights import AIInsightModule
from app.database import SessionLocal, engine
from app.models import Analytics, Base, Call

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

fake = Faker()
ai_module = AIInsightModule()

# Sample conversation templates for generating synthetic transcripts
CONVERSATION_TEMPLATES = [
    {
        "scenario": "Product Demo Call",
        "template": """Agent: Good morning {customer_name}, thank you for your interest in our product.
Customer: Hi, I've been looking for a solution to help with {business_problem}.
Agent: Perfect! Our {product_name} is designed specifically for that. Let me show you how it works.
Customer: That sounds interesting. What makes it different from {competitor}?
Agent: Great question! The key difference is {unique_value_prop}. Would you like to see a demo?
Customer: Yes, that would be helpful.
Agent: Excellent! I'll schedule a follow-up demo for you. What's your timeline for implementation?
Customer: We're looking at {timeline}. What about pricing?
Agent: I'll prepare a custom quote based on your needs. Can we schedule that demo for next week?
Customer: {closing_response}""",
    },
    {
        "scenario": "Support Call",
        "template": """Agent: Hello {customer_name}, I understand you're having an issue with {product_feature}.
Customer: Yes, it's been {problem_duration} and I can't figure out what's wrong.
Agent: I'm sorry to hear that. Let me help you resolve this quickly. Can you tell me exactly what happens when you try to {action}?
Customer: {problem_description}
Agent: I see the issue. This is actually a common problem that we can fix easily. Let me walk you through the solution.
Customer: Okay, I'm ready.
Agent: First, you'll want to {solution_step_1}. Then {solution_step_2}.
Customer: Got it, let me try that... Oh wow, that worked! Thank you so much.
Agent: Wonderful! Is there anything else I can help you with today?
Customer: {additional_request}""",
    },
    {
        "scenario": "Sales Follow-up",
        "template": """Agent: Hi {customer_name}, I wanted to follow up on our conversation about {product_name}.
Customer: {initial_response}
Agent: I understand your concerns about {concern}. Many of our clients had similar worries initially.
Customer: What did they find after implementation?
Agent: They typically see {benefit_1} within the first month and {benefit_2} by quarter end.
Customer: That's impressive. What about the learning curve?
Agent: We provide comprehensive training and our support team is available 24/7. Most users are productive within {timeframe}.
Customer: {price_objection}
Agent: I understand budget is important. Let's discuss ROI - most clients see payback within {roi_timeframe}.
Customer: {final_response}""",
    },
]

# Sample data for template filling
SAMPLE_DATA = {
    "business_problem": [
        "managing customer data",
        "tracking sales pipeline",
        "automating workflows",
        "improving team communication",
    ],
    "product_name": ["SalesFlow Pro", "DataSync Plus", "WorkflowMaster", "TeamConnect"],
    "competitor": ["Salesforce", "HubSpot", "Pipedrive", "Monday.com"],
    "unique_value_prop": [
        "advanced AI analytics",
        "seamless integrations",
        "intuitive interface",
        "comprehensive reporting",
    ],
    "timeline": [
        "Q2 next year",
        "within 3 months",
        "as soon as possible",
        "by end of year",
    ],
    "closing_response": [
        "Sounds good!",
        "I need to discuss with my team first.",
        "Let me think about it.",
        "Yes, let's move forward.",
    ],
    "product_feature": [
        "reporting dashboard",
        "data export",
        "user permissions",
        "mobile app",
    ],
    "problem_duration": [
        "happening since yesterday",
        "going on for a week",
        "started this morning",
        "occurring intermittently",
    ],
    "action": ["generate reports", "export data", "log in", "sync data"],
    "problem_description": [
        "I get an error message",
        "the page won't load",
        "data isn't syncing",
        "nothing happens when I click",
    ],
    "solution_step_1": [
        "clear your browser cache",
        "check your permissions",
        "refresh the data",
        "restart the application",
    ],
    "solution_step_2": [
        "try the action again",
        "contact admin if issues persist",
        "wait 5 minutes for sync",
        "check the updated settings",
    ],
    "additional_request": [
        "No, that's all. Thanks!",
        "Can you show me how to do X?",
        "What about feature Y?",
        "I have another question.",
    ],
    "initial_response": [
        "I'm still interested",
        "I have some concerns",
        "My team needs more info",
        "We're comparing options",
    ],
    "concern": [
        "price",
        "implementation time",
        "training requirements",
        "integration complexity",
    ],
    "benefit_1": [
        "30% time savings",
        "improved accuracy",
        "better collaboration",
        "increased sales",
    ],
    "benefit_2": [
        "ROI of 200%",
        "90% user adoption",
        "50% cost reduction",
        "doubled productivity",
    ],
    "timeframe": ["one week", "two weeks", "a few days", "less than a week"],
    "price_objection": [
        "It seems expensive",
        "Budget is tight",
        "Need to justify cost",
        "Comparing with cheaper options",
    ],
    "roi_timeframe": ["6 months", "one year", "3 months", "9 months"],
    "final_response": [
        "Let me discuss with my team",
        "I'm ready to move forward",
        "Send me the proposal",
        "I need more time to decide",
    ],
}


def generate_synthetic_transcript() -> Dict[str, Any]:
    """Generate a synthetic sales call transcript."""
    template = random.choice(CONVERSATION_TEMPLATES)
    customer_name = fake.first_name()

    # Fill template with random sample data
    transcript = template["template"]
    transcript = transcript.format(
        customer_name=customer_name,
        **{key: random.choice(values) for key, values in SAMPLE_DATA.items()},
    )

    # Generate call metadata
    start_time = fake.date_time_between(start_date="-30d", end_date="now")
    duration = random.randint(300, 3600)  # 5 to 60 minutes

    call_data = {
        "call_id": f"CALL_{fake.unique.random_int(min=100000, max=999999)}",
        "agent_id": f"AGENT_{random.randint(1, 20)}",
        "customer_id": f"CUST_{fake.unique.random_int(min=10000, max=99999)}",
        "language": "en",
        "start_time": start_time,
        "duration_seconds": duration,
        "transcript": transcript,
        "scenario": template["scenario"],
    }

    return call_data


async def process_call_insights(call_data: Dict[str, Any]) -> Dict[str, Any]:
    """Process AI insights for a call."""
    try:
        # Generate embedding
        embedding = ai_module.generate_embedding(call_data["transcript"])

        # Analyze sentiment
        sentiment_score = ai_module.analyze_sentiment(call_data["transcript"])

        # Calculate agent talk ratio
        talk_ratio = ai_module.calculate_agent_talk_ratio(call_data["transcript"])

        call_data.update(
            {
                "embedding": embedding,
                "customer_sentiment_score": sentiment_score,
                "agent_talk_ratio": talk_ratio,
            }
        )

        return call_data

    except Exception as e:
        logger.error(f"Error processing insights for call {call_data['call_id']}: {e}")
        return call_data


async def save_call_to_db(call_data: Dict[str, Any], db: Session):
    """Save call data to database."""
    try:
        call = Call(
            call_id=call_data["call_id"],
            agent_id=call_data["agent_id"],
            customer_id=call_data["customer_id"],
            language=call_data["language"],
            start_time=call_data["start_time"],
            duration_seconds=call_data["duration_seconds"],
            transcript=call_data["transcript"],
            agent_talk_ratio=call_data.get("agent_talk_ratio"),
            customer_sentiment_score=call_data.get("customer_sentiment_score"),
            embedding=call_data.get("embedding"),
        )

        db.add(call)
        db.commit()
        logger.info(f"Saved call {call_data['call_id']} to database")

    except Exception as e:
        logger.error(f"Error saving call {call_data['call_id']}: {e}")
        db.rollback()


async def save_raw_transcript(call_data: Dict[str, Any]):
    """Save raw transcript to JSON file for reproducibility."""
    try:
        os.makedirs("data/raw_transcripts", exist_ok=True)

        filename = f"data/raw_transcripts/{call_data['call_id']}.json"
        with open(filename, "w") as f:
            # Make datetime serializable
            serializable_data = {**call_data}
            if isinstance(serializable_data["start_time"], datetime):
                serializable_data["start_time"] = serializable_data[
                    "start_time"
                ].isoformat()

            json.dump(serializable_data, f, indent=2)

    except Exception as e:
        logger.error(f"Error saving raw transcript for {call_data['call_id']}: {e}")


async def ingest_batch(batch_size: int = 10):
    """Ingest a batch of calls with AI processing."""
    db = SessionLocal()

    try:
        tasks = []
        for i in range(batch_size):
            call_data = generate_synthetic_transcript()

            # Save raw transcript
            await save_raw_transcript(call_data)

            # Process AI insights
            call_with_insights = await process_call_insights(call_data)

            # Save to database
            await save_call_to_db(call_with_insights, db)

            logger.info(f"Processed call {i+1}/{batch_size}")

    except Exception as e:
        logger.error(f"Error in batch ingestion: {e}")
    finally:
        db.close()


async def update_analytics(db: Session):
    """Update the analytics table with aggregated data."""
    try:
        # Get all agents
        agents = db.query(Call.agent_id).distinct().all()

        for (agent_id,) in agents:
            # Calculate aggregated metrics
            calls = db.query(Call).filter(Call.agent_id == agent_id).all()

            if calls:
                avg_sentiment = sum(
                    call.customer_sentiment_score or 0 for call in calls
                ) / len(calls)
                avg_talk_ratio = sum(
                    call.agent_talk_ratio or 0 for call in calls
                ) / len(calls)
                total_calls = len(calls)

                # Update or create analytics record
                analytics = (
                    db.query(Analytics).filter(Analytics.agent_id == agent_id).first()
                )

                if analytics:
                    analytics.avg_sentiment = avg_sentiment
                    analytics.avg_talk_ratio = avg_talk_ratio
                    analytics.total_calls = total_calls
                    analytics.last_updated = datetime.utcnow()
                else:
                    analytics = Analytics(
                        agent_id=agent_id,
                        avg_sentiment=avg_sentiment,
                        avg_talk_ratio=avg_talk_ratio,
                        total_calls=total_calls,
                    )
                    db.add(analytics)

        db.commit()
        logger.info("Analytics updated successfully")

    except Exception as e:
        logger.error(f"Error updating analytics: {e}")
        db.rollback()


async def main():
    """Main ingestion pipeline."""
    logger.info("Starting data ingestion pipeline...")

    # Create tables if they don't exist
    Base.metadata.create_all(bind=engine)

    # Ingest calls in batches
    total_calls = 200
    batch_size = 20
    batches = (total_calls + batch_size - 1) // batch_size

    for batch_num in range(batches):
        logger.info(f"Processing batch {batch_num + 1}/{batches}")
        current_batch_size = min(batch_size, total_calls - batch_num * batch_size)
        await ingest_batch(current_batch_size)

        # Small delay to avoid overwhelming the system
        await asyncio.sleep(1)

    # Update analytics
    db = SessionLocal()
    try:
        await update_analytics(db)
    finally:
        db.close()

    logger.info(f"Ingestion complete! Processed {total_calls} calls.")


if __name__ == "__main__":
    asyncio.run(main())
