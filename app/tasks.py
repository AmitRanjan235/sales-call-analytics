import logging
import os
from datetime import datetime

from celery import Celery
from dotenv import load_dotenv
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker

from app.models import Analytics, Call

load_dotenv()

# Configure Celery
redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
celery_app = Celery("sales_analytics", broker=redis_url, backend=redis_url)

# Database setup - use the same configuration as the main app
database_url = os.getenv("DATABASE_URL", "sqlite:///./data/sales_analytics.db")

# SQLite-specific configuration
if database_url.startswith("sqlite"):
    engine = create_engine(
        database_url,
        connect_args={
            "check_same_thread": False
        },  # Allow SQLite to be used with multiple threads
    )
else:
    engine = create_engine(database_url)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@celery_app.task
def recalculate_analytics():
    """Background task to recalculate agent analytics nightly."""
    logger.info("Starting nightly analytics recalculation...")

    db = SessionLocal()
    try:
        # Get all agents
        agents = db.query(Call.agent_id).distinct().all()
        updated_count = 0

        for (agent_id,) in agents:
            # Calculate aggregated metrics for this agent
            calls = db.query(Call).filter(Call.agent_id == agent_id).all()

            if calls:
                # Calculate averages
                sentiment_scores = [
                    call.customer_sentiment_score
                    for call in calls
                    if call.customer_sentiment_score is not None
                ]
                talk_ratios = [
                    call.agent_talk_ratio
                    for call in calls
                    if call.agent_talk_ratio is not None
                ]

                avg_sentiment = (
                    sum(sentiment_scores) / len(sentiment_scores)
                    if sentiment_scores
                    else None
                )
                avg_talk_ratio = (
                    sum(talk_ratios) / len(talk_ratios) if talk_ratios else None
                )
                total_calls = len(calls)

                # Update or create analytics record
                analytics = (
                    db.query(Analytics).filter(Analytics.agent_id == agent_id).first()
                )

                if analytics:
                    object.__setattr__(analytics, "avg_sentiment", avg_sentiment)
                    object.__setattr__(analytics, "avg_talk_ratio", avg_talk_ratio)
                    object.__setattr__(analytics, "total_calls", total_calls)
                    object.__setattr__(analytics, "last_updated", datetime.utcnow())
                else:
                    analytics = Analytics(
                        agent_id=agent_id,
                        avg_sentiment=avg_sentiment,
                        avg_talk_ratio=avg_talk_ratio,
                        total_calls=total_calls,
                    )
                    db.add(analytics)

                updated_count += 1

        db.commit()
        logger.info(
            f"Analytics recalculation complete. Updated {updated_count} agents."
        )
        return {"status": "success", "updated_agents": updated_count}

    except Exception as e:
        db.rollback()
        logger.error(f"Error recalculating analytics: {e}")
        return {"status": "error", "message": str(e)}
    finally:
        db.close()


@celery_app.task
def cleanup_old_calls(days_to_keep: int = 90):
    """Background task to cleanup old call records."""
    logger.info(f"Starting cleanup of calls older than {days_to_keep} days...")

    db = SessionLocal()
    try:
        from datetime import timedelta

        cutoff_date = datetime.utcnow() - timedelta(days=days_to_keep)

        # Delete old calls
        deleted_count = db.query(Call).filter(Call.start_time < cutoff_date).delete()
        db.commit()

        logger.info(f"Cleanup complete. Deleted {deleted_count} old calls.")
        return {"status": "success", "deleted_calls": deleted_count}

    except Exception as e:
        db.rollback()
        logger.error(f"Error during cleanup: {e}")
        return {"status": "error", "message": str(e)}
    finally:
        db.close()


# Configure periodic tasks
celery_app.conf.beat_schedule = {
    "recalculate-analytics-nightly": {
        "task": "app.tasks.recalculate_analytics",
        "schedule": 60.0 * 60.0 * 24.0,  # Run every 24 hours
    },
    "cleanup-old-calls-weekly": {
        "task": "app.tasks.cleanup_old_calls",
        "schedule": 60.0 * 60.0 * 24.0 * 7.0,  # Run every week
        "kwargs": {"days_to_keep": 90},
    },
}

celery_app.conf.timezone = "UTC"

if __name__ == "__main__":
    celery_app.start()
