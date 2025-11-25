from django.views.generic import TemplateView
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache


class SignupView(TemplateView):
    """Signup selection page - shows Explorer and Join Artist options"""
    template_name = 'signup_selection.html'
    
    def get_template_names(self):
        # If package is provided, redirect to artist signup (old flow)
        package = self.request.GET.get('package', '')
        if package:
            return ['signup.html']
        # Otherwise show the selection page
        return ['signup_selection.html']
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        package = self.request.GET.get('package', '')
        if package:
            context['package'] = package
        return context


class SignupExplorerView(TemplateView):
    """Explorer signup page for general users"""
    template_name = 'signup_explorer.html'
    
    def post(self, request, *args, **kwargs):
        # Handle form submission here
        # For now, just render the form
        return self.get(request, *args, **kwargs)


@method_decorator(never_cache, name='dispatch')
class ExplorerDashboardView(TemplateView):
    """Explorer dashboard page"""
    template_name = 'explorer_dashboard.html'
