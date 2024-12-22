import logging
from celery import shared_task
from .monitor import monitor_for_user, check_and_store_ssl_domain_status
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

@shared_task(bind=True)
def scheduled_ssl_domain_check(self):
    logger.info("Executing scheduled_ssl_domain_check...")
    try:
        users = User.objects.all() 
        for user in users:
            check_and_store_ssl_domain_status(user.id)
        logger.info("SSL and Domain Status Check completed successfully.")
    except Exception as e:
        logger.error(f"Error during SSL and Domain Check: {e}")