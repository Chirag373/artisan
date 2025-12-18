from django.urls import path
from . import views

app_name = 'custom_admin'

urlpatterns = [
    path('login/', views.AdminLoginView.as_view(), name='login'),
    path('logout/', views.AdminLogoutView.as_view(), name='logout'),
    path('', views.AdminDashboardView.as_view(), name='dashboard'),
    path('users/', views.UserListView.as_view(), name='user_list'),
    path('users/<int:user_id>/', views.UserDetailView.as_view(), name='user_detail'),
    path('pricing/', views.PlanPricingView.as_view(), name='plan_pricing'),
    path('promo-codes/', views.StripePromoView.as_view(), name='stripe_promo'),
    path('payments/', views.PaymentListView.as_view(), name='payment_list'),
    path('visitors/', views.VisitorStatsView.as_view(), name='visitor_stats'),
    path('announcements/', views.AnnouncementView.as_view(), name='announcements'),
]
