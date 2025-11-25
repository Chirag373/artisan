from django.urls import path
from . import views, api_views

# No app_name to maintain backward compatibility with existing URL references
urlpatterns = [
    # Template views - these are under /artists/ prefix from main urls.py
    path('join/', views.JoinArtistView.as_view(), name='artists_join'),
    path('dashboard/', views.ArtistDashboardView.as_view(), name='artist_dashboard'),
    path('profile/<slug:slug>/', views.ViewProfileView.as_view(), name='artists_view_profile'),
    
    # API endpoints
    path('api/signup/', api_views.ArtistSignupAPIView.as_view(), name='api_signup_artist'),
    path('api/dashboard/', api_views.ArtistDashboardAPIView.as_view(), name='api_artist_dashboard'),
    path('api/featured/', api_views.FeaturedArtistsAPIView.as_view(), name='api_featured_artists'),
    path('api/<slug:slug>/', api_views.ArtistProfileDetailAPIView.as_view(), name='api_artist_profile_detail'),
]
