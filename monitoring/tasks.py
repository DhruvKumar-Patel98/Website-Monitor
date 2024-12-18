import logging
from celery import shared_task
from .monitor import monitor_for_user
from django.contrib.auth.models import User


logger = logging.getLogger(__name__)

@shared_task(bind=True)
def scheduled_monitoring(self):
    logger.info("Executing scheduled_monitoring...")
    try:
        users = User.objects.all() 
        for user in users:
            monitor_for_user(user.id)      
        logger.info("Monitoring completed successfully.")
    except Exception as e:
        logger.error(f"Error during monitoring: {e}")
