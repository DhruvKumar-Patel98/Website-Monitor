from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.shortcuts import redirect


def home_view(request):
    return render(request, 'monitoring/home.html')

@login_required(login_url='/login')
def dashboard(request):
    return render(request, 'monitoring/dashboard.html')

@login_required(login_url='/login')
def notification(request):
    return render(request, 'monitoring/notification.html')

@login_required(login_url='/login')
def page_status(request):
    return render(request, 'monitoring/page_status.html')

@login_required(login_url='/login')
def settings(request):
    return render(request, 'monitoring/settings.html')


@login_required(login_url='/login')
def logout_view(request):
    logout(request)
    return redirect('/')