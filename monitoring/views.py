import json
from django.utils import timezone 
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.views import View
from .form import MonitoringCheckForm
from .models import MonitoringCheck, MonitoringResult, SSLDomainStatus
from .tasks import scheduled_monitoring
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from .form import COUNTRIES
from django.http import JsonResponse, HttpResponseNotAllowed


def home_view(request):
    return render(request, 'monitoring/home.html')

@login_required(login_url='/login')
def dashboard(request):
    monitoring_checks = MonitoringCheck.objects.filter(user=request.user)  # Fetch monitoring checks
    results = MonitoringResult.objects.filter(user=request.user).order_by('-checked_at')  # Fetch monitoring results
    scheduled_monitoring.delay()
    form = MonitoringCheckForm()
    return render(request, 'monitoring/dashboard.html', {'monitoring_checks': monitoring_checks, 'results': results, 'form': form})

def chart_data(request, check_id):
    try:
        results = MonitoringResult.objects.filter(monitoring_check__id=check_id).order_by('location_checked', 'checked_at')
        
        grouped_data = {}
        for result in results:
            location = result.location_checked
            if location not in grouped_data:
                grouped_data[location] = {
                    'labels': [],
                    'data': [],
                    'statuses': [],
                }
            grouped_data[location]['labels'].append(result.checked_at.strftime('%Y-%m-%d %H:%M:%S'))
            grouped_data[location]['data'].append(result.response_time)
            grouped_data[location]['statuses'].append(result.status)
        return JsonResponse(grouped_data)
    except Exception as e:
        print(f"Error during fetching chart data: {e}")
        return JsonResponse({'error': 'Error fetching chart data.'}, status=500)
    
class AllChartDataView(View):
    def get(self, request):
        data = []
        monitoring_checks = MonitoringCheck.objects.all()
        
        for check in monitoring_checks:
            chart_data = {
                'id': check.id,
                'name_of_check': check.name_of_check,
                'labels': [],
                'data': [],
                'statuses': [],
            }
            
            results = check.monitoringresult_set.order_by('checked_at')
            for result in results:
                chart_data['labels'].append(result.checked_at.isoformat())
                chart_data['data'].append(result.response_time)
                chart_data['statuses'].append(result.status)
            
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
            monitoring_check.user = request.user  
            monitoring_check.last_checked = timezone.now() 
            custom_port = request.POST.get('port')
            if custom_port:
                monitoring_check.port = int(custom_port)
            else:
                if monitoring_check.check_type == 'http':
                    monitoring_check.port = 80
                elif monitoring_check.check_type == 'https':
                    monitoring_check.port = 443
            monitoring_check.save()
            return redirect('dashboard')
        else:
            print("Invalid", form.errors)
    else:
        form = MonitoringCheckForm()
    
    return render(request, 'monitoring/settings.html', {'form': form})


@login_required(login_url='/login')
def account(request):
    logout(request)
    return redirect('/')

@csrf_exempt
@require_http_methods(["GET", "PUT", "DELETE"])
def get_or_update_check_data(request, id):
    try:
        check = MonitoringCheck.objects.get(id=id)
        if request.method == "GET":
            location_to_check = check.location_to_check.split(',') if check.location_to_check else []
            data = {
                'name_of_check': check.name_of_check,
                'check_interval': check.check_interval,
                'check_type': check.check_type,
                'url': check.url,
                'port': check.port,
                'contact_detail': check.contact_detail,
                'location_to_check': location_to_check,
            }
            return JsonResponse(data)
        
        elif request.method == "PUT":
            data = json.loads(request.body)
            check.name_of_check = data.get('name_of_check', check.name_of_check)
            check.check_interval = data.get('check_interval', check.check_interval)
            check.check_type = data.get('check_type', check.check_type)
            check.url = data.get('url', check.url)
            check.port = data.get('port', check.port)
            check.contact_detail = data.get('contact_detail', check.contact_detail)
            check.location_to_check = ','.join(data.get('location_to_check', []))
            check.save()
            return JsonResponse({"message": "Check updated successfully.", "status": "success"})
        
        elif request.method == "DELETE":
            check = get_object_or_404(MonitoringCheck, id=id)
            title = check.name_of_check
            check.delete()
            return JsonResponse({"message": f"{title} deleted successfully.", "status": "success"})
        else:
            return HttpResponseNotAllowed(["DELETE"])
        
    except MonitoringCheck.DoesNotExist:
        return JsonResponse({'error': 'Check not found'}, status=404)
    except Exception as e:
        print(f"Error in get_or_update_check_data: {e}")
        return JsonResponse({'error': str(e)}, status=500)

def edit_check(request):
    if request.method == 'POST':
        check_id = request.POST.get('check_id')
        check = get_object_or_404(MonitoringCheck, id=check_id)
        check.name_of_check = request.POST.get('name_of_check')
        check.check_interval = int(request.POST.get('check_interval'))
        check.check_type = request.POST.get('check_type')
        check.url = request.POST.get('url')
        check.contact_detail = request.POST.get('contact_detail')
        check.location_to_check = ','.join(request.POST.getlist('location_to_check'))  # Handle multiple countries
        custom_port = request.POST.get('port')
        if custom_port:
            check.port = int(custom_port)
        else:
            if check.check_type == 'http':
                check.port = 80
            elif check.check_type == 'https':
                check.port = 443
        check.save()
        return redirect('dashboard')
    
@csrf_exempt
@require_http_methods(["PUT"])
def update_check(request, check_id):
    try:
        check = MonitoringCheck.objects.get(id=check_id)
        data = json.loads(request.body)
        
        check.name_of_check = data.get("name_of_check", check.name_of_check)
        check.check_interval = data.get("check_interval", check.check_interval)
        check.check_type = data.get("check_type", check.check_type)
        check.url = data.get("url", check.url)
        check.contact_detail = data.get("contact_detail", check.contact_detail)
        location_to_check = data.get("location_to_check", [])
        check.location_to_check = ','.join(location_to_check)
        custom_port = data.get("port")
        if custom_port:
            check.port = int(custom_port)
        else:
            if check.check_type == 'http':
                check.port = 80
            elif check.check_type == 'https':
                check.port = 443
        
        check.save()
        return JsonResponse({"message": "Check updated successfully."})
    except MonitoringCheck.DoesNotExist:
        return JsonResponse({"error": "Check not found."}, status=404)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
    
def port_ping_status_data(request, check_id):
    try:
        results = MonitoringResult.objects.filter(monitoring_check__id=check_id).order_by('location_checked', 'checked_at')
        
        grouped_data = {}
        for result in results:
            location = result.location_checked
            if location not in grouped_data:
                grouped_data[location] = {
                    'ping_status': [],
                    'port_status': [],
                    'timestamps': []
                }
            grouped_data[location]['ping_status'].append(result.ping_status)
            grouped_data[location]['port_status'].append(result.port_status)
            grouped_data[location]['timestamps'].append(result.checked_at.strftime('%Y-%m-%d %H:%M:%S'))
        
        return JsonResponse(grouped_data)
    except Exception as e:
        print(f"Error during fetching port and ping status data: {e}")
        return JsonResponse({'error': 'Error fetching port and ping status data.'}, status=500)

def ssl_domain_status_data(request, check_id):
    try:
        results = SSLDomainStatus.objects.filter(monitoring_check__id=check_id).order_by('last_checked')

        grouped_data = {
            'ssl_status': [],
            'ssl_expiry_date': [],
            'domain_expiry_date': [],
            'timestamps': []
        }

        for result in results:
            grouped_data['ssl_status'].append(result.ssl_status)
            grouped_data['ssl_expiry_date'].append(result.ssl_expiry_date.strftime('%Y-%m-%d'))
            grouped_data['domain_expiry_date'].append(result.domain_expiry_date.strftime('%Y-%m-%d') if result.domain_expiry_date else "N/A")
            grouped_data['timestamps'].append(result.last_checked.strftime('%Y-%m-%d %H:%M:%S'))

        return JsonResponse(grouped_data)
    except Exception as e:
        print(f"Error during fetching SSL/Domain status data: {e}")
        return JsonResponse({'error': 'Error fetching SSL/Domain status data.'}, status=500)
