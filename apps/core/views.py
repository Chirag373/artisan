from django.shortcuts import render, redirect

def home(request):
    """Homepage view"""
    return render(request, 'homepage.html')

def view_profile(request, slug=None):
    """View profile page"""
    context = {'slug': slug} if slug else {}
    return render(request, 'view_profile.html', context)

def login_view(request):
    """Login page view"""
    return render(request, 'login.html')

def join_artist(request):
    """Join as artist page - shows pricing plans"""
    # If accessed directly (not from signup selection or dashboard), redirect to signup
    # Check if 'from' parameter is set or if referrer suggests it came from signup or dashboard
    from_param = request.GET.get('from', '')
    referer = request.META.get('HTTP_REFERER', '')
    
    # Allow access if:
    # 1. 'from' parameter is set
    # 2. Referrer contains 'signup' or 'dashboard' (user came from signup flow or was redirected from dashboard)
    # 3. User is authenticated (they might have been redirected from artist_dashboard)
    if not from_param and 'signup' not in referer and 'dashboard' not in referer and not request.user.is_authenticated:
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

from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist

@login_required
@never_cache
def artist_dashboard(request):
    """Artist dashboard page"""
    try:
        # Check if user has an artist profile
        if not hasattr(request.user, 'artist_profile'):
            return redirect('join_artist')
        # Try to access the artist_profile to ensure it exists
        artist_profile = request.user.artist_profile
    except (ObjectDoesNotExist, AttributeError):
        return redirect('join_artist')
        
    return render(request, 'artists/artist_dashboard.html')

def services(request):
    """Services page view"""
    return render(request, 'services.html')