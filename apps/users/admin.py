from django.contrib import admin
from .models import ExplorerProfile, Bookmark


@admin.register(ExplorerProfile)
class ExplorerProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone_number', 'city', 'state')
    search_fields = ('user__username', 'user__email', 'city', 'state')
    list_filter = ('state',)


@admin.register(Bookmark)
class BookmarkAdmin(admin.ModelAdmin):
    list_display = ('explorer', 'artist', 'created_at')
    search_fields = ('explorer__username', 'artist__artist_name')
    list_filter = ('created_at',)
    raw_id_fields = ('explorer', 'artist')
