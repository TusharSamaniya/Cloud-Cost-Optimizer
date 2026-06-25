import logging
import os
import sys

# Make sure the ml/ folder is importable from the scheduler
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..')))

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.db.session import SessionLocal
from app.db.models.user import User

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_all_active_users():
    """Returns all users who have AWS credentials saved."""
    db = SessionLocal()
    try:
        # Only sync users who have actually connected their AWS account
        users = db.query(User).filter(User.aws_access_key.isnot(None)).all()
        return users
    finally:
        db.close()


async def daily_sync_and_pipeline():
    """
    This runs automatically every night at 2:00 AM.
    For each user with AWS credentials:
      1. Syncs fresh data from AWS (or mock)
      2. Runs the full ML pipeline on that fresh data
    """
    logger.info("=" * 50)
    logger.info("Starting automated nightly sync...")

    # ✅ FIX 3: import here (inside the function) to avoid circular imports at startup
    from ml.pipeline import run_full_pipeline

    users = get_all_active_users()
    logger.info(f"Found {len(users)} active user(s) to sync.")

    for user in users:
        logger.info(f"Processing user_id={user.id} ({user.email})")
        try:
            # Step 1 — sync AWS data into the database
            # (Your existing sync logic writes to the Resource table)
            # sync_aws_data(user.id)  ← uncomment when you wire sync route

            # Step 2 — run all 4 ML models on the fresh data
            run_full_pipeline(user.id)                 # ✅ FIX 4: called correctly
            logger.info(f"Pipeline complete for user_id={user.id}")

        except Exception as e:
            # One user failing must NOT stop other users from being processed
            logger.error(f"Failed for user_id={user.id}: {e}")
            continue

    logger.info("Nightly sync complete.")
    logger.info("=" * 50)


# ✅ FIX 3: only ONE scheduler, only ONE job added — the correct async function
scheduler = AsyncIOScheduler()
scheduler.add_job(
    daily_sync_and_pipeline,
    trigger='cron',
    hour=2,
    minute=0,
    id='nightly_sync',          # named ID makes it easy to inspect/cancel
    replace_existing=True,
)