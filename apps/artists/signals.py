from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from django.core.cache import cache
from .models import ArtistProfile, PortfolioImage


def clear_featured_api_caches():
    """
    Clears all paginated API cache keys for featured artists.
    Since we use hash-based keys, we need to delete known patterns.
    For simplicity, we delete commonly used combinations.
    """
    import hashlib
    
    # Clear common pagination patterns for both homepage and elite creators
    for featured_only in [True, False]:
        for page in range(1, 11):  # Clear first 10 pages
            for page_size in [6, 9, 12]:  # Common page sizes
                key_parts = f"featured_api_p{page}_ps{page_size}_fo{featured_only}"
                cache_key = f"api_featured_artists_{hashlib.md5(key_parts.encode()).hexdigest()}"
                cache.delete(cache_key)


@receiver(pre_save, sender=ArtistProfile)
def capture_old_slug(sender, instance, **kwargs):
    """
    Capture the old slug before save to ensure we invalidate the correct cache key.
    """
    if instance.pk:
        try:
            old_instance = ArtistProfile.objects.get(pk=instance.pk)
            instance._old_slug = old_instance.slug
        except ArtistProfile.DoesNotExist:
            instance._old_slug = None
    else:
        instance._old_slug = None


@receiver(post_save, sender=ArtistProfile)
@receiver(post_delete, sender=ArtistProfile)
def invalidate_artist_cache(sender, instance, **kwargs):
    """
    Clears cache keys whenever an ArtistProfile is saved, updated, or deleted.
    This includes both view-level and API-level caches.
    """
    # Clear view-level caches (legacy)
    cache.delete('homepage_featured_artists')
    cache.delete('elite_creators_list')
    
    # Clear API-level caches
    clear_featured_api_caches()
    
    # Clear specific artist profile API cache - both old and new slug
    old_slug = getattr(instance, '_old_slug', None)
    new_slug = instance.slug
    
    # Delete cache for old slug (if it changed)
    if old_slug:
        cache.delete(f'artist_featured_work_{old_slug}')
        cache.delete(f'api_artist_profile_{old_slug}')
    
    # Delete cache for new/current slug
    if new_slug:
        cache.delete(f'artist_featured_work_{new_slug}')
        cache.delete(f'api_artist_profile_{new_slug}')


@receiver(post_save, sender=PortfolioImage)
@receiver(post_delete, sender=PortfolioImage)
def invalidate_portfolio_cache(sender, instance, **kwargs):
    """
    Clears portfolio cache when portfolio images are changed.
    """
    try:
        if instance.artist and instance.artist.slug:
            slug = instance.artist.slug
            # Clear view-level cache
            cache.delete(f'artist_featured_work_{slug}')
            # Clear API-level cache (includes portfolio in response)
            cache.delete(f'api_artist_profile_{slug}')
            # Clear featured API caches (portfolio images shown on elite creators page)
            clear_featured_api_caches()
    except Exception:
        # Avoid breaking save if something is wrong with relationships
        pass
