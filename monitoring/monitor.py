from django.utils import timezone
from monitoring.models import MonitoringCheck, MonitoringResult
import requests
from django.contrib.auth.models import User

def monitor_websites_for_user(user_id):
    user = User.objects.get(id=user_id) 
    checks = MonitoringCheck.objects.filter(user=user) 
    now = timezone.now().replace(tzinfo=None) 

    for check in checks:
        try:
            last_checked_naive = check.last_checked.replace(tzinfo=None) if check.last_checked else None

            time_difference = (now - last_checked_naive).total_seconds() / 60 if last_checked_naive else check.check_interval

            if time_difference >= check.check_interval:
                url_to_check = check.url
                response = requests.get(url_to_check, timeout=5)
                status = response.status_code
                response_time = response.elapsed.total_seconds() * 1000  # in milliseconds

                MonitoringResult.objects.create(
                    user=check.user,
                    url=check.url,
                    status=status,
                    response_time=response_time,
                    checked_at=timezone.now()  # Save timezone-aware 'checked_at'
                )

                check.last_checked = timezone.now()
                check.save()
        except Exception as e:
            MonitoringResult.objects.create(
                user=check.user,
                url=check.url,
                status='Error',
                response_time=0,
                checked_at=timezone.now()
            )
