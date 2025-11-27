from django.urls import path
from . import views

# No app_name to maintain backward compatibility with existing URL references
urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('services/', views.ServicesView.as_view(), name='services'),
    path('terms/', views.TermsView.as_view(), name='terms'),
    path('refund/', views.RefundView.as_view(), name='refund'),
    path('content-policy/', views.ContentPolicyView.as_view(), name='content_policy'),
    path('privacy/', views.PrivacyView.as_view(), name='privacy'),
]
