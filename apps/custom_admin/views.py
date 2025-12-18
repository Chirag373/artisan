from django.views.generic import View, TemplateView
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta
import json

from apps.artists.models import ArtistProfile
from apps.users.models import ExplorerProfile
from apps.subscriptions.models import Subscription
from .models import PlanPricing, SiteVisitor, Announcement


class AdminRequiredMixin(UserPassesTestMixin):
    """Mixin to ensure only admin users can access the view."""
    login_url = '/custom-admin/login/'
    
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_staff


class AdminLoginView(View):
    """Custom admin login page."""
    template_name = 'custom_admin/login.html'
    
    def get(self, request):
        if request.user.is_authenticated and request.user.is_staff:
            return redirect('custom_admin:dashboard')
        return render(request, self.template_name)
    
    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None and user.is_staff:
            login(request, user)
            return JsonResponse({'success': True, 'redirect': '/custom-admin/'})
        
        return JsonResponse({
            'success': False, 
            'error': 'Invalid credentials or insufficient permissions.'
        }, status=400)


class AdminLogoutView(View):
    """Admin logout."""
    def get(self, request):
        logout(request)
        return redirect('custom_admin:login')
    
    def post(self, request):
        logout(request)
        return redirect('custom_admin:login')


class AdminDashboardView(AdminRequiredMixin, TemplateView):
    """Main admin dashboard."""
    template_name = 'custom_admin/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # User counts by role
        total_users = User.objects.exclude(is_staff=True).count()
        artist_count = ArtistProfile.objects.count()
        explorer_count = ExplorerProfile.objects.count()
        
        # Subscription stats
        active_subscriptions = Subscription.objects.filter(is_active=True).count()
        
        # Plan breakdown
        plan_stats = Subscription.objects.filter(is_active=True).values('plan_name').annotate(
            count=Count('id')
        )
        
        # Recent visitors (last 24 hours)
        yesterday = timezone.now() - timedelta(hours=24)
        recent_visitors = SiteVisitor.objects.filter(visited_at__gte=yesterday).count()
        unique_visitors = SiteVisitor.objects.filter(
            visited_at__gte=yesterday
        ).values('ip_address').distinct().count()
        
        # Recent users
        recent_users = User.objects.exclude(
            is_staff=True
        ).order_by('-date_joined')[:5]
        
        context.update({
            'total_users': total_users,
            'artist_count': artist_count,
            'explorer_count': explorer_count,
            'active_subscriptions': active_subscriptions,
            'plan_stats': {p['plan_name']: p['count'] for p in plan_stats},
            'recent_visitors': recent_visitors,
            'unique_visitors': unique_visitors,
            'recent_users': recent_users,
        })
        
        return context


class UserListView(AdminRequiredMixin, TemplateView):
    """List all users with filtering."""
    template_name = 'custom_admin/user_list.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        role_filter = self.request.GET.get('role', 'all')
        search = self.request.GET.get('search', '')
        
        # Base queryset - exclude admin users and admin email
        users = User.objects.exclude(is_staff=True).exclude(is_superuser=True)
        
        if search:
            users = users.filter(
                Q(username__icontains=search) |
                Q(email__icontains=search) |
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search)
            )
        
        # Build user list with role info
        user_list = []
        for user in users.order_by('-date_joined'):
            role = 'unknown'
            subscription = None
            
            if hasattr(user, 'artist_profile'):
                role = 'artist'
                try:
                    subscription = user.subscription
                except Subscription.DoesNotExist:
                    subscription = None
            elif hasattr(user, 'explorer_profile'):
                role = 'explorer'
            
            if role_filter != 'all' and role != role_filter:
                continue
                
            user_list.append({
                'user': user,
                'role': role,
                'subscription': subscription,
            })
        
        context.update({
            'users': user_list,
            'role_filter': role_filter,
            'search': search,
        })
        
        return context


class UserDetailView(AdminRequiredMixin, TemplateView):
    """User detail page."""
    template_name = 'custom_admin/user_detail.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_id = kwargs.get('user_id')
        user = get_object_or_404(User, id=user_id)
        
        # Don't show admin users
        if user.is_staff or user.is_superuser:
            return redirect('custom_admin:user_list')
        
        role = 'unknown'
        profile = None
        subscription = None
        
        if hasattr(user, 'artist_profile'):
            role = 'artist'
            profile = user.artist_profile
            try:
                subscription = user.subscription
            except Subscription.DoesNotExist:
                pass
        elif hasattr(user, 'explorer_profile'):
            role = 'explorer'
            profile = user.explorer_profile
        
        context.update({
            'detail_user': user,
            'role': role,
            'profile': profile,
            'subscription': subscription,
        })
        
        return context


class PlanPricingView(AdminRequiredMixin, TemplateView):
    """Manage plan pricing."""
    template_name = 'custom_admin/plan_pricing.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Ensure default plans exist
        default_plans = [
            {'plan_name': 'basic', 'price_cents': 2900, 'description': 'Basic plan for new artists'},
            {'plan_name': 'express', 'price_cents': 5900, 'description': 'Express plan with more features'},
            {'plan_name': 'premium', 'price_cents': 9900, 'description': 'Premium plan with all features'},
        ]
        
        for plan in default_plans:
            PlanPricing.objects.get_or_create(
                plan_name=plan['plan_name'],
                defaults=plan
            )
        
        context['plans'] = PlanPricing.objects.all().order_by('price_cents')
        return context
    
    def post(self, request):
        plan_id = request.POST.get('plan_id')
        price_dollars = request.POST.get('price')
        description = request.POST.get('description', '')
        
        try:
            plan = PlanPricing.objects.get(id=plan_id)
            plan.price_cents = int(float(price_dollars) * 100)
            plan.description = description
            plan.save()
            return JsonResponse({'success': True})
        except (PlanPricing.DoesNotExist, ValueError) as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)


class StripePromoView(AdminRequiredMixin, TemplateView):
    """Stripe promo code management - redirects to Stripe dashboard."""
    template_name = 'custom_admin/stripe_promo.html'


class PaymentListView(AdminRequiredMixin, TemplateView):
    """List all payments/subscriptions."""
    template_name = 'custom_admin/payment_list.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        subscriptions = Subscription.objects.select_related('user').order_by('-created_at')
        
        context['subscriptions'] = subscriptions
        return context


class VisitorStatsView(AdminRequiredMixin, TemplateView):
    """Visitor statistics."""
    template_name = 'custom_admin/visitor_stats.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Stats for different time periods
        now = timezone.now()
        periods = {
            'today': now - timedelta(hours=24),
            'week': now - timedelta(days=7),
            'month': now - timedelta(days=30),
        }
        
        stats = {}
        for period_name, start_date in periods.items():
            visitors = SiteVisitor.objects.filter(visited_at__gte=start_date)
            stats[period_name] = {
                'total': visitors.count(),
                'unique': visitors.values('ip_address').distinct().count(),
            }
        
        # Top pages
        top_pages = SiteVisitor.objects.filter(
            visited_at__gte=periods['week']
        ).values('path').annotate(
            count=Count('id')
        ).order_by('-count')[:10]
        
        context.update({
            'stats': stats,
            'top_pages': top_pages,
        })
        
        return context


class AnnouncementView(AdminRequiredMixin, TemplateView):
    """Manage announcements."""
    template_name = 'custom_admin/announcements.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Ensure default announcement exists
        announcement, created = Announcement.objects.get_or_create(
            location='join_artist',
            defaults={
                'label': 'Special Offer',
                'content': '<p>We are running soft opening, if you sign up elite plan, use promo code <strong>NEWARTIST60</strong> for the first 60 signup for only 1$ per month, for the next 3 months , if you continue to join... the $3 will be credited, if not join, we will refund the 3$, (For elite plan only )</p><p>Amd , for first come first serve basis, Another line, or, use <strong>NEWARTIST30</strong> to get 30% discount, for the 3 months ,</p>',
                'is_active': False
            }
        )
        context['announcement'] = announcement
        return context

    def post(self, request):
        content = request.POST.get('content', '')
        label = request.POST.get('label', '')
        is_active = request.POST.get('is_active') == 'on'

        try:
            announcement = Announcement.objects.get(location='join_artist')
            announcement.content = content
            announcement.label = label
            announcement.is_active = is_active
            announcement.save()
            return JsonResponse({'success': True})
        except Announcement.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Announcement not found'}, status=404)
