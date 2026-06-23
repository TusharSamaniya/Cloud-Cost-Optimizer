import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.db.session import SessionLocal
from app.db.models.user import User

# Set up a logger so we can see the scheduler working in the terminal
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def daily_sync():
    """This function runs automatically in the background."""
    logger.info("Starting automated daily sync...")
    
    # We need to open a fresh database connection for the background worker
    db = SessionLocal()
    try:
        # Find all users who have actually saved their AWS keys
        active_users = db.query(User).filter(User.aws_access_key.isnot(None)).all()
        
        for user in active_users:
            logger.info(f"Syncing data for user ID: {user.id}")
            # In a fully connected app, we would call our sync_cloud_data logic here!
            
    except Exception as e:
        logger.error(f"Error during background sync: {e}")
    finally:
        db.close() # Always close the door behind you!
        
    logger.info("Automated daily sync complete.")

# Create the scheduler and tell it to run our function at 2:00 AM every day
scheduler = AsyncIOScheduler()
scheduler.add_job(daily_sync, 'cron', hour=2, minute=0)