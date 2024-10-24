from django import forms
from .models import MonitoringCheck  # Import the model
class MonitoringCheckForm(forms.ModelForm):
    class Meta:
        model = MonitoringCheck
        fields = ['name_of_check', 'check_interval', 'check_type', 'url', 'contact_detail', 'location_to_check']
        widgets = {
            'check_interval': forms.NumberInput(attrs={'min': 5, 'max': 60, 'value': 30})  # Define min/max for interval here
        }