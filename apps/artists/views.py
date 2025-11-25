from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.core.exceptions import ObjectDoesNotExist


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


def view_profile(request, slug=None):
    """View profile page"""
    context = {'slug': slug} if slug else {}
    return render(request, 'view_profile.html', context)
