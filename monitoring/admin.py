from django.contrib import admin
from .models import MonitoringCheck, MonitoringResult

admin.site.register(MonitoringCheck) 
admin.site.register(MonitoringResult)  

