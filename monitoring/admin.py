from django.contrib import admin
from .models import MonitoringCheck, MonitoringResult, SSLDomainStatus

admin.site.register(MonitoringCheck) 
admin.site.register(MonitoringResult) 
admin.site.register(SSLDomainStatus)  

