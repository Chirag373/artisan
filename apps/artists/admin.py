from django.contrib import admin
from .models import ArtistProfile


@admin.register(ArtistProfile)
class ArtistProfileAdmin(admin.ModelAdmin):
    list_display = ('artist_name', 'user', 'subscription_plan', 'location_city', 'location_state', 'is_featured', 'rating')
    search_fields = ('artist_name', 'user__username', 'user__email', 'location_city', 'location_state')
    list_filter = ('subscription_plan', 'is_featured', 'location_state')
    prepopulated_fields = {'slug': ('artist_name',)}
