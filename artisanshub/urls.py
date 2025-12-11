"""
URL configuration for artisanshub project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from apps.artists.views import ViewProfileView, JoinArtistView
from apps.artists.api_views import (
    FeaturedArtistsAPIView,
    ArtistSignupAPIView,
    ArtistVerifyOTPAPIView,
    ArtistDashboardAPIView,
    ArtistProfileDetailAPIView,
    RateArtistAPIView,
    PortfolioUploadAPIView,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('custom-admin/', include('apps.custom_admin.urls', namespace='custom_admin')),
    
    path('', include('apps.core.urls')),
    
    path('', include('apps.users.urls')),
    
    path('artists/', include('apps.artists.urls')),
    path('subscriptions/', include('apps.subscriptions.urls')),
    
    # API endpoints at root level
    path('api/featured-artists/', FeaturedArtistsAPIView.as_view(), name='api_featured_artists'),
    path('api/signup/artist/', ArtistSignupAPIView.as_view(), name='api_signup_artist'),
    path('api/signup/artist/verify/', ArtistVerifyOTPAPIView.as_view(), name='api_signup_artist_verify'),
    path('api/artist/dashboard/', ArtistDashboardAPIView.as_view(), name='api_artist_dashboard'),
    path('api/artists/<slug:slug>/', ArtistProfileDetailAPIView.as_view(), name='api_artist_profile_detail'),
    path('api/artists/<slug:slug>/rate/', RateArtistAPIView.as_view(), name='api_rate_artist'),
    path('api/portfolio/upload/', PortfolioUploadAPIView.as_view(), name='api_portfolio_upload'),
    path('api/portfolio/<int:image_id>/', PortfolioUploadAPIView.as_view(), name='api_portfolio_delete'),
    path('artist/', ViewProfileView.as_view(), name='view_profile'),
    path('artist/<slug:slug>/', ViewProfileView.as_view(), name='view_profile_with_slug'),
    path('join-artist/', JoinArtistView.as_view(), name='join_artist'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    # Test route for 404 page
    urlpatterns.append(path('404/', TemplateView.as_view(template_name='404.html')))
