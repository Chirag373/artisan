from django.shortcuts import render, redirect
from django.views.decorators.cache import never_cache


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


@never_cache
def explorer_dashboard(request):
    """Explorer dashboard page"""
    return render(request, 'explorer_dashboard.html')
