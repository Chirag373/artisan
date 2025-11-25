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
