from django.contrib import admin
from .models import ExplorerProfile


@admin.register(ExplorerProfile)
class ExplorerProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone_number', 'city', 'state')
    search_fields = ('user__username', 'user__email', 'city', 'state')
    list_filter = ('state',)
