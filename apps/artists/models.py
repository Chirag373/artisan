from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.core.validators import MinValueValidator, MaxValueValidator


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
    short_bio = models.CharField(max_length=255, blank=True, help_text="Short bio for cards and summaries")
    
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
    website_url = models.URLField(blank=True, max_length=500, help_text="Personal website URL")
    contact_email = models.EmailField(blank=True, max_length=255, help_text="Public contact email")

    profile_image = models.ImageField(upload_to='artist_profiles/', blank=True, null=True, help_text="Profile image (400x400px)")
    banner_image = models.ImageField(upload_to='artist_banners/', blank=True, null=True, help_text="Banner image")

    subscription_plan = models.CharField(max_length=20, choices=SUBSCRIPTION_CHOICES, default='basic')
    rating = models.DecimalField(max_digits=3, decimal_places=1, null=True, blank=True)
    is_featured = models.BooleanField(default=False)
    is_visible = models.BooleanField(default=False, help_text="Toggle to show/hide profile from public listings")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def check_completeness(self):
        """
        Checks if all mandatory fields are filled.
        Returns (is_complete, missing_fields)
        """
        mandatory_fields = [
            'artist_name', 'slug', 'location_state', 'location_city', 
            'short_bio', 'full_bio', 'categories', 'profile_image'
        ]
        missing_fields = []
        
        for field in mandatory_fields:
            value = getattr(self, field)
            if not value:
                # Special handling for list/json fields if needed, but 'not []' works for empty list
                missing_fields.append(field)
            elif field == 'profile_image' and not value:
                missing_fields.append(field)
                
        return len(missing_fields) == 0, missing_fields

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


class Rating(models.Model):
    """
    Rating model for explorers to rate artists.
    Only explorers can rate artists.
    """
    artist = models.ForeignKey(ArtistProfile, on_delete=models.CASCADE, related_name='ratings')
    explorer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='given_ratings')
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Rating from 1 to 5 stars"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('artist', 'explorer')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.explorer.username} rated {self.artist.artist_name}: {self.rating} stars"


class PortfolioImage(models.Model):
    """
    Images for the artist's featured work portfolio.
    """
    artist = models.ForeignKey(ArtistProfile, on_delete=models.CASCADE, related_name='portfolio_images')
    image = models.ImageField(upload_to='portfolio_images/')
    caption = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Portfolio image for {self.artist.artist_name}"


class PendingArtist(models.Model):
    """
    Temporary storage for artist signup data until payment is confirmed.
    """
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=150)
    password = models.CharField(max_length=128)  # Hashed password
    package = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Pending: {self.email}"
