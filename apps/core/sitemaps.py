from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from apps.artists.models import ArtistProfile

class StaticViewSitemap(Sitemap):
    priority = 0.5
    changefreq = 'weekly'
    protocol = 'https'

    def items(self):
        return [
            'home',
            'login',
            'premium_artists',
            'services',
            'terms',
            'refund',
            'content_policy',
            'privacy',
            'join_artist',
        ]

    def location(self, item):
        return reverse(item)

class ArtistProfileSitemap(Sitemap):
    priority = 0.8
    changefreq = 'daily'
    protocol = 'https'

    def items(self):
        return ArtistProfile.objects.filter(is_visible=True).order_by('-created_at')

    def location(self, obj):
        return reverse('view_profile_with_slug', args=[obj.slug])

    def lastmod(self, obj):
        return obj.updated_at
