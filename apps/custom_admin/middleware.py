from .models import SiteVisitor


class VisitorTrackingMiddleware:
    """
    Middleware to track public visitors on the website.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Skip tracking for admin, static, and media paths
        path = request.path
        skip_paths = ['/admin/', '/static/', '/media/', '/api/', '/custom-admin/']
        
        should_skip = any(path.startswith(p) for p in skip_paths)
        
        if not should_skip and not request.user.is_authenticated:
            # Get client IP
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                ip = x_forwarded_for.split(',')[0].strip()
            else:
                ip = request.META.get('REMOTE_ADDR', '0.0.0.0')
            
            # Track the visit
            SiteVisitor.objects.create(
                ip_address=ip,
                user_agent=request.META.get('HTTP_USER_AGENT', '')[:500],
                path=path[:500],
                referrer=request.META.get('HTTP_REFERER', '')[:500] or None,
                session_key=request.session.session_key
            )

        response = self.get_response(request)
        return response
