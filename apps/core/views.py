from django.shortcuts import render


def home(request):
    """Homepage view"""
    return render(request, 'homepage.html')


def login_view(request):
    """Login page view"""
    return render(request, 'login.html')


def services(request):
    """Services page view"""
    return render(request, 'services.html')
