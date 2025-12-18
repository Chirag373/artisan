from django.db import models


class PlanPricing(models.Model):
    """
    Model to store and manage subscription plan pricing.
    """
    PLAN_CHOICES = [
        ('basic', 'Basic'),
        ('express', 'Express'),
        ('premium', 'Premium'),
    ]

    plan_name = models.CharField(max_length=50, choices=PLAN_CHOICES, unique=True)
    price_cents = models.IntegerField(help_text="Price in cents (e.g., 2900 for $29.00)")
    description = models.TextField(blank=True)
    features = models.JSONField(default=list, blank=True, help_text="List of plan features")
    is_active = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Plan Pricing"
        verbose_name_plural = "Plan Pricing"

    def __str__(self):
        return f"{self.get_plan_name_display()} - ${self.price_cents / 100:.2f}/mo"

    @property
    def price_dollars(self):
        return self.price_cents / 100


class Announcement(models.Model):
    """
    Model to manage site-wide or page-specific announcements.
    """
    LOCATION_CHOICES = [
        ('join_artist', 'Join Artist Page'),
    ]
    location = models.CharField(max_length=50, choices=LOCATION_CHOICES, default='join_artist', unique=True)
    label = models.CharField(max_length=50, blank=True, help_text="Label for the announcement (e.g. Christmas Offer)")
    content = models.TextField(help_text="HTML content allowed")
    is_active = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Announcement for {self.get_location_display()}"


class SiteVisitor(models.Model):
    """
    Model to track public visitors on the website.
    """
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True)
    path = models.CharField(max_length=500)
    referrer = models.URLField(blank=True, null=True)
    visited_at = models.DateTimeField(auto_now_add=True)
    session_key = models.CharField(max_length=40, blank=True, null=True)

    class Meta:
        ordering = ['-visited_at']

    def __str__(self):
        return f"{self.ip_address} - {self.path} at {self.visited_at}"
