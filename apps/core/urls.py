from django.urls import path
from . import views

# No app_name to maintain backward compatibility with existing URL references
urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('services/', views.ServicesView.as_view(), name='services'),
]
