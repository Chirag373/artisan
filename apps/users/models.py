from django.db import models
from django.contrib.auth.models import User


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
