from rest_framework import serializers
from .models import ArtistProfile


class ArtistProfileSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source='user.email', read_only=True)
    
    class Meta:
        model = ArtistProfile
        fields = [
            'artist_name', 'slug', 'full_bio', 'location_city', 'location_state',
            'product_keywords', 'seo_tags', 'categories',
            'etsy_url', 'shopify_url', 'instagram_url', 'tiktok_url',
            'profile_image', 'banner_image',
            'subscription_plan', 'email', 'rating', 'is_featured'
        ]
        read_only_fields = ['subscription_plan', 'email']

    def update(self, instance, validated_data):
        # Categories are expected to be a list
        if 'categories' in validated_data:
            # Ensure it's a list (though JSONField/ListField usually handles this)
            pass
            
        return super().update(instance, validated_data)
