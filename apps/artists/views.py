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
        from_param = request.GET.get('from', '')
        referer = request.META.get('HTTP_REFERER', '')
        
        if not from_param and 'signup' not in referer and 'dashboard' not in referer and not request.user.is_authenticated:
            return redirect('signup')
        
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            from apps.custom_admin.models import PlanPricing
            plans = PlanPricing.objects.all()
            context['pricing'] = {p.plan_name: p.price_dollars for p in plans}
        except:
            context['pricing'] = {'basic': 29, 'express': 59, 'premium': 99}
        return context


@method_decorator(never_cache, name='dispatch')
class ArtistDashboardView(LoginRequiredMixin, TemplateView):
    """Artist dashboard page"""
    template_name = 'artists/artist_dashboard.html'
    
    def dispatch(self, request, *args, **kwargs):
        try:
            if not hasattr(request.user, 'artist_profile'):
                return redirect('join_artist')
            artist_profile = request.user.artist_profile
        except (ObjectDoesNotExist, AttributeError):
            return redirect('join_artist')
            
        return super().dispatch(request, *args, **kwargs)


class ViewProfileView(TemplateView):
    """
    View profile page - data is loaded via JavaScript API calls.
    The API endpoint handles caching of the full JSON response.
    We only pass the slug to the template for the JS to use.
    """
    template_name = 'view_profile.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        slug = kwargs.get('slug')
        if slug:
            context['slug'] = slug
            # Artist data for SEO meta tags (minimal DB query)
            try:
                from .models import ArtistProfile
                context['artist'] = ArtistProfile.objects.only(
                    'artist_name', 'short_bio', 'full_bio', 'categories',
                    'profile_image', 'etsy_url', 'shopify_url', 'instagram_url', 'tiktok_url'
                ).get(slug=slug)
            except ArtistProfile.DoesNotExist:
                pass
        return context
