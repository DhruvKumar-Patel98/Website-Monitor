from django import forms
from .models import MonitoringCheck 
import pycountry

COUNTRIES = [('us', 'United States'),
        ('ca', 'Canada'),
        ('uk', 'United Kingdom'),]

class MonitoringCheckForm(forms.ModelForm):
    location_to_check = forms.MultipleChoiceField(
        choices=COUNTRIES,
        widget=forms.SelectMultiple(attrs={'class': 'form-control'})
    )
    class Meta:
        model = MonitoringCheck
        fields = ['name_of_check', 'check_interval', 'check_type', 'url', 'contact_detail', 'location_to_check']
        widgets = {
            'check_interval': forms.NumberInput(attrs={'min': 5, 'max': 60, 'value': 30})  # Define min/max for interval here
        }
    def clean_location_to_check(self):
        return ','.join(self.cleaned_data['location_to_check'])