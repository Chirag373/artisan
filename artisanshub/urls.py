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
from django.urls import path
from apps.core import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('profile/', views.view_profile, name='view_profile'),
    path('login/', views.login_view, name='login'),
    path('join-artist/', views.join_artist, name='join_artist'),
    path('signup/', views.signup, name='signup'),
    path('signup/explorer/', views.signup_explorer, name='signup_explorer'),
    path('explorer/dashboard/', views.explorer_dashboard, name='explorer_dashboard'),
    path('artist/dashboard/', views.artist_dashboard, name='artist_dashboard'),
]
