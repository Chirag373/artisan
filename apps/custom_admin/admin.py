from django.contrib import admin
from .models import PlanPricing, SiteVisitor


@admin.register(PlanPricing)
class PlanPricingAdmin(admin.ModelAdmin):
    list_display = ['plan_name', 'price_dollars', 'is_active', 'updated_at']
    list_filter = ['is_active', 'plan_name']


@admin.register(SiteVisitor)
class SiteVisitorAdmin(admin.ModelAdmin):
    list_display = ['ip_address', 'path', 'visited_at']
    list_filter = ['visited_at']
    search_fields = ['ip_address', 'path']
