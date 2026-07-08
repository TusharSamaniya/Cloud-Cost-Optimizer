import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.db.session import SessionLocal
from app.db.models.user import User

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_all_active_users():
    """Returns all users who have AWS credentials saved."""
    db = SessionLocal()
    try:
        # Only sync users who have connected their AWS account
        users = db.query(User).filter(User.aws_access_key.isnot(None)).all()
        return users
    finally:
        db.close()

async def daily_sync_and_pipeline():
    """
    Runs automatically every night at 2:00 AM.
    """
    logger.info("=" * 50)
    logger.info("Starting automated nightly sync...")

    # ✅ CORRECTED: Import directly from the 'ml' folder
    # This works because your Root Directory is set to '/backend'
    try:
        from ml.pipeline import run_full_pipeline
    except ImportError as e:
        logger.error(f"Failed to import ml.pipeline: {e}")
        return

    users = get_all_active_users()
    logger.info(f"Found {len(users)} active user(s) to sync.")

    for user in users:
        logger.info(f"Processing user_id={user.id} ({user.email})")
        try:
            # Run the ML pipeline
            run_full_pipeline(user.id)
            logger.info(f"Pipeline complete for user_id={user.id}")
        except Exception as e:
            logger.error(f"Failed for user_id={user.id}: {e}")
            continue

    logger.info("Nightly sync complete.")
    logger.info("=" * 50)

# Initialize and schedule
scheduler = AsyncIOScheduler()
scheduler.add_job(
    daily_sync_and_pipeline,
    trigger='cron',
    hour=2,
    minute=0,
    id='nightly_sync',
    replace_existing=True,
)