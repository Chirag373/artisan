from django.views.generic import TemplateView


class HomeView(TemplateView):
    """Homepage view"""
    template_name = 'homepage.html'


class LoginView(TemplateView):
    """Login page view"""
    template_name = 'login.html'


class ServicesView(TemplateView):
    """Services page view"""
    template_name = 'services.html'


class TermsView(TemplateView):
    """Terms of Use page view"""
    template_name = 'terms.html'


class RefundView(TemplateView):
    """Refund & Cancellation Policy page view"""
    template_name = 'refund.html'


class ContentPolicyView(TemplateView):
    """Artist & Content Policy page view"""
    template_name = 'content-policy.html'


class PrivacyView(TemplateView):
    """Privacy Policy page view"""
    template_name = 'privacy.html'


class PremiumArtistsView(TemplateView):
    """Premium Artists page view"""
    template_name = 'premium_artists.html'
