from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify

class ExplorerProfile(models.Model):
    """
    Profile for general users (Explorers) who browse and purchase art.
    Fields correspond to the 'Explorer Dashboard' template.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='explorer_profile')
    
    # Contact Information
    phone_number = models.CharField(max_length=20, blank=True)
    
    # Address Information
    street_number = models.CharField(max_length=100, blank=True)
    street_address = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    zip_code = models.CharField(max_length=20, blank=True)
    
    # Discovery & Promotions
    promotion_keywords = models.TextField(
        blank=True, 
        help_text="Keywords for promotions the user is interested in (e.g., Pokemon, Barbie)"
    )

    def __str__(self):
        return f"Explorer: {self.user.username}"


class ArtistProfile(models.Model):
    """
    Profile for Artists. Includes business details, SEO settings, and subscription info.
    Fields correspond to 'Artist Dashboard' and 'View Profile' templates.
    """
    # Subscription Plans from join_artist.html
    SUBSCRIPTION_CHOICES = [
        ('basic', 'Basic ($29/mo)'),
        ('express', 'Express ($59/mo)'),
        ('premium', 'Premium ($99/mo)'),
    ]

    # Categories from artist_dashboard.html
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
    
    # Basic Information
    artist_name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, max_length=255, help_text="URL-friendly version of artist name")
    full_bio = models.TextField(help_text="Full biography for SEO", blank=True) # Corresponds to 'full_bio' in template
    
    # Location fields (Required for homepage search and profile view)
    location_city = models.CharField(max_length=100, blank=True)
    location_state = models.CharField(max_length=100, blank=True)
    
    # Product Entry (Internal Search Data)
    product_keywords = models.TextField(
        blank=True, 
        help_text="Internal use only - product item names for search matching"
    )
    
    # SEO Settings
    seo_tags = models.CharField(
        max_length=500, 
        blank=True, 
        help_text="Comma-separated keywords for SEO"
    )
    
    # Categories (Stored as JSON list to support checkboxes in dashboard)
    categories = models.JSONField(default=list, blank=True, help_text="List of selected categories")

    # External Links
    etsy_url = models.URLField(blank=True, max_length=500)
    shopify_url = models.URLField(blank=True, max_length=500)
    instagram_url = models.URLField(blank=True, max_length=500)
    tiktok_url = models.URLField(blank=True, max_length=500)

    # Images (Using URLFields to match template inputs)
    profile_image_url = models.URLField(max_length=500, help_text="URL to profile image (400x400px)")
    banner_image_url = models.URLField(max_length=500, blank=True, help_text="URL to banner image")

    # Business Logic
    subscription_plan = models.CharField(max_length=20, choices=SUBSCRIPTION_CHOICES, default='basic')
    rating = models.DecimalField(max_digits=3, decimal_places=1, default=5.0)
    is_featured = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        # Auto-generate slug from artist_name if not provided
        if not self.slug:
            self.slug = slugify(self.artist_name)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Artist: {self.artist_name}"