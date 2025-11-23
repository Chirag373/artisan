from django.shortcuts import render, redirect

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
    """Join as artist page - shows pricing plans"""
    # If accessed directly (not from signup selection), redirect to signup
    # Check if 'from' parameter is set or if referrer suggests it came from signup
    from_param = request.GET.get('from', '')
    referer = request.META.get('HTTP_REFERER', '')
    
    # If no 'from' parameter and referrer doesn't contain 'signup', redirect to signup
    if not from_param and 'signup' not in referer:
        return redirect('signup')
    
    # Otherwise show the pricing page
    return render(request, 'join_artist.html')

def signup(request):
    """Signup selection page - shows Explorer and Join Artist options"""
    # If package is provided, redirect to artist signup (old flow)
    package = request.GET.get('package', '')
    if package:
        context = {
            'package': package,
        }
        return render(request, 'signup.html', context)
    # Otherwise show the selection page
    return render(request, 'signup_selection.html')

def signup_explorer(request):
    """Explorer signup page for general users"""
    if request.method == 'POST':
        # Handle form submission here
        # For now, just render the form
        pass
    return render(request, 'signup_explorer.html')

def signup_artist(request):
    """Artist signup page (when coming from join-artist page)"""
    package = request.GET.get('package', '')
    context = {
        'package': package,
    }
    return render(request, 'signup.html', context)

from django.views.decorators.cache import never_cache

@never_cache
def explorer_dashboard(request):
    """Explorer dashboard page"""
    return render(request, 'explorer_dashboard.html')

@never_cache
def artist_dashboard(request):
    """Artist dashboard page"""
    return render(request, 'artists/artist_dashboard.html')