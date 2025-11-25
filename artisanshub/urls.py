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
from apps.artists import views as artist_views

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Core app (shared/base views)
    path('', include('apps.core.urls')),
    
    # Users app (Explorer logic and authentication)
    path('', include('apps.users.urls')),
    
    # Artists app
    path('artists/', include('apps.artists.urls')),
    
    # Legacy profile routes (for backward compatibility)
    path('profile/', artist_views.view_profile, name='view_profile'),
    path('profile/<slug:slug>/', artist_views.view_profile, name='view_profile_with_slug'),
    path('join-artist/', artist_views.join_artist, name='join_artist'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
