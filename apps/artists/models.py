from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify


class ArtistProfile(models.Model):
    """
    Profile for Artists. Includes business details, SEO settings, and subscription info.
    Fields correspond to 'Artist Dashboard' and 'View Profile' templates.
    """
    SUBSCRIPTION_CHOICES = [
        ('basic', 'Basic ($29/mo)'),
        ('express', 'Express ($59/mo)'),
        ('premium', 'Premium ($99/mo)'),
    ]

    CATEGORY_CHOICES = [
        ('stickers', 'Stickers'),
        ('fan_art', 'Fan Art'),
        ('keychains', 'Keychains'),
        ('prints', 'Prints'),
        ('t-shirts', 'T-Shirts'),
        ('posters', 'Posters'),
        ('pins', 'Pins'),
        ('mugs', 'Mugs'),
        ('other', 'Other'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='artist_profile')
    
    artist_name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, max_length=255, help_text="URL-friendly version of artist name")
    full_bio = models.TextField(help_text="Full biography for SEO", blank=True)
    
    location_city = models.CharField(max_length=100, blank=True)
    location_state = models.CharField(max_length=100, blank=True)
    
    product_keywords = models.TextField(
        blank=True, 
        help_text="Internal use only - product item names for search matching"
    )
    
    seo_tags = models.CharField(
        max_length=500, 
        blank=True, 
        help_text="Comma-separated keywords for SEO"
    )
    
    categories = models.JSONField(default=list, blank=True, help_text="List of selected categories")

    etsy_url = models.URLField(blank=True, max_length=500)
    shopify_url = models.URLField(blank=True, max_length=500)
    instagram_url = models.URLField(blank=True, max_length=500)
    tiktok_url = models.URLField(blank=True, max_length=500)

    profile_image = models.ImageField(upload_to='artist_profiles/', blank=True, null=True, help_text="Profile image (400x400px)")
    banner_image = models.ImageField(upload_to='artist_banners/', blank=True, null=True, help_text="Banner image")

    subscription_plan = models.CharField(max_length=20, choices=SUBSCRIPTION_CHOICES, default='basic')
    rating = models.DecimalField(max_digits=3, decimal_places=1, default=5.0)
    is_featured = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        # Auto-generate slug only if it doesn't exist
        if not self.slug:
            self.slug = slugify(self.artist_name)
        # If slug is provided but empty string, generate from artist_name
        elif self.slug == '':
            self.slug = slugify(self.artist_name)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Artist: {self.artist_name}"
