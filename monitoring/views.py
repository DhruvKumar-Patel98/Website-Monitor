from django.utils import timezone 
from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.shortcuts import redirect
from .form import MonitoringCheckForm
from .models import MonitoringCheck, MonitoringResult
from .tasks import scheduled_monitoring

def home_view(request):
    return render(request, 'monitoring/home.html')

@login_required(login_url='/login')
def dashboard(request):
    monitoring_checks = MonitoringCheck.objects.filter(user=request.user)  # Fetch monitoring checks
    results = MonitoringResult.objects.filter(user=request.user).order_by('-checked_at')  # Fetch monitoring results
    scheduled_monitoring.delay()
    return render(request, 'monitoring/dashboard.html', {'monitoring_checks': monitoring_checks, 'results': results})


@login_required(login_url='/login')
def notification(request):
    return render(request, 'monitoring/notification.html')

@login_required(login_url='/login')
def page_status(request):
    return render(request, 'monitoring/page_status.html')

@login_required(login_url='/login')
def settings(request):
    if request.method == 'POST':
        form = MonitoringCheckForm(request.POST)
        if form.is_valid():
            monitoring_check = form.save(commit=False)
            monitoring_check.user = request.user  # Link the monitoring check to the logged-in user
            monitoring_check.last_checked = timezone.now()  # Set the current time when creating a new check
            monitoring_check.save()  # Save the form data to the database
            return redirect('dashboard')  # Redirect to the dashboard after saving
        else:
            print("Invalid", form.errors)  # For debugging
    else:
        form = MonitoringCheckForm()
    
    return render(request, 'monitoring/settings.html', {'form': form})


@login_required(login_url='/login')
def account(request):
    logout(request)
    return redirect('/')