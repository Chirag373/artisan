from django.urls import path
from . import views

# No app_name to maintain backward compatibility with existing URL references
urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('services/', views.services, name='services'),
]
