from django.shortcuts import render

def home(request):
    """Homepage view"""
    return render(request, 'homepage.html')

def view_profile(request):
    """View profile page"""
    return render(request, 'view_profile.html')

def login_view(request):
    """Login page view"""
    return render(request, 'login.html')

def join_artist(request):
    """Join as artist page"""
    return render(request, 'join_artist.html')

def signup(request):
    """Signup page with package selection"""
    package = request.GET.get('package', '')
    context = {
        'package': package,
    }
    return render(request, 'signup.html', context)

