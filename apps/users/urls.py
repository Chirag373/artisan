from django.urls import path
from . import views, api_views

# No app_name to maintain backward compatibility with existing URL references
urlpatterns = [
    # Template views
    path('signup/', views.SignupView.as_view(), name='signup'),
    path('signup/explorer/', views.SignupExplorerView.as_view(), name='signup_explorer'),
    path('explorer/dashboard/', views.ExplorerDashboardView.as_view(), name='explorer_dashboard'),
    
    # API endpoints
    path('api/signup/explorer/', api_views.ExplorerSignupAPIView.as_view(), name='api_signup_explorer'),
    path('api/login/', api_views.CustomTokenObtainPairView.as_view(), name='api_login'),
    path('api/explorer/profile/', api_views.ExplorerProfileDetailView.as_view(), name='api_explorer_profile'),
]
