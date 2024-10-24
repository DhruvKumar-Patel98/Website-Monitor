from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from django.conf import settings

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'website_monitor.settings')

# Create a new Celery application instance
app = Celery('website_monitor')
app.conf.enable_utc = False
app.conf.update(timezone = 'America/Chicago')
app.config_from_object(settings, namespace='CELERY')
app.conf.broker_connection_retry_on_startup = True

app.autodiscover_tasks(['monitoring']) 
