from django.utils import timezone 
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.views import View
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

def chart_data(request, check_id):
    try:
        results = MonitoringResult.objects.filter(monitoring_check__id=check_id).order_by('checked_at')
        data = {
            'labels': [result.checked_at.strftime('%Y-%m-%d %H:%M:%S') for result in results],
            'data': [result.response_time for result in results]
        }
        return JsonResponse(data)
    except Exception as e:
        print(f"Error during fetching chart data: {e}")
        return JsonResponse({'error': 'Error fetching chart data.'}, status=500)
    
class AllChartDataView(View):
    def get(self, request):
        data = []
        monitoring_checks = MonitoringCheck.objects.all()
        
        for check in monitoring_checks:
            # Collect the relevant data for each check
            chart_data = {
                'id': check.id,
                'name_of_check': check.name_of_check,
                'labels': [],  # Replace with your actual labels
                'data': [],    # Replace with your actual data points
            }
            # Populate labels and data based on your model's monitoring results
            results = check.monitoringresult_set.all()
            for result in results:
                chart_data['labels'].append(result.checked_at.isoformat())  # or your preferred format
                chart_data['data'].append(result.response_time)
            
            data.append(chart_data)
        
        return JsonResponse(data, safe=False)

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