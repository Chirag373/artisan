from django.shortcuts import redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.core.exceptions import ObjectDoesNotExist


class JoinArtistView(TemplateView):
    """Join as artist page - shows pricing plans"""
    template_name = 'join_artist.html'
    
    def dispatch(self, request, *args, **kwargs):
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
        return super().dispatch(request, *args, **kwargs)


@method_decorator(never_cache, name='dispatch')
class ArtistDashboardView(LoginRequiredMixin, TemplateView):
    """Artist dashboard page"""
    template_name = 'artists/artist_dashboard.html'
    
    def dispatch(self, request, *args, **kwargs):
        try:
            # Check if user has an artist profile
            if not hasattr(request.user, 'artist_profile'):
                return redirect('join_artist')
            # Try to access the artist_profile to ensure it exists
            artist_profile = request.user.artist_profile
        except (ObjectDoesNotExist, AttributeError):
            return redirect('join_artist')
            
        return super().dispatch(request, *args, **kwargs)


class ViewProfileView(TemplateView):
    """View profile page"""
    template_name = 'view_profile.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        slug = kwargs.get('slug')
        if slug:
            context['slug'] = slug
        return context
