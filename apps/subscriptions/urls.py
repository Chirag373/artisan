from django.urls import path
from . import views

urlpatterns = [
    path('success/', views.PaymentSuccessView.as_view(), name='payment_success'),
    path('cancel/', views.PaymentCancelView.as_view(), name='payment_cancel'),
    path('portal/', views.SubscriptionPortalView.as_view(), name='subscription_portal'),
]
