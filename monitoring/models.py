from django.db import models
from django.contrib.auth.models import User
from datetime import timedelta
from django.utils import timezone 

class MonitoringCheck(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name_of_check = models.CharField(max_length=255)
    check_interval = models.IntegerField(default=30)  # Interval in minutes
    check_type = models.CharField(max_length=10, choices=[('http', 'HTTP'), ('https', 'HTTPS')])
    url = models.URLField()
    port = models.IntegerField(default=443)
    contact_detail = models.EmailField()
    location_to_check = models.TextField(blank=True, null=True) 
    last_checked = models.DateTimeField(default=timezone.now) 

    def __str__(self):
        return self.name_of_check

    def should_run_check(self):
        if not self.last_checked:
            return True
        now = timezone.now()
        next_check_time = self.last_checked + timedelta(minutes=self.check_interval)
        return now >= next_check_time


class MonitoringResult(models.Model):
    monitoring_check = models.ForeignKey(MonitoringCheck, on_delete=models.CASCADE, related_name='monitoringresult_set')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    url = models.CharField(max_length=255) 
    status = models.CharField(max_length=50)
    response_time = models.FloatField()
    ping_status = models.CharField(max_length=50, null=True, blank=True)
    port_status = models.CharField(max_length=50, null=True, blank=True)
    checked_at = models.DateTimeField(auto_now_add=True)
    location_checked = models.CharField(max_length=100, null=True, blank=True) 

    def __str__(self):
        return f"{self.url} - {self.status} at {self.checked_at} from {self.location_checked}"

class SSLDomainStatus(models.Model):
    monitoring_check = models.ForeignKey('MonitoringCheck', on_delete=models.CASCADE)
    ssl_status = models.CharField(max_length=50)  # e.g., Active or Expired
    ssl_expiry_date = models.DateTimeField(null=True, blank=True)
    domain_expiry_date = models.DateTimeField(null=True, blank=True)
    last_checked = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.monitoring_check.name_of_check} - Status"
