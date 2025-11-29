from rest_framework import serializers
from .models import ArtistProfile, Rating, PortfolioImage


class PortfolioImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PortfolioImage
        fields = ['id', 'image', 'caption', 'created_at']
        read_only_fields = ['created_at']


class ArtistProfileSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source='user.email', read_only=True)
    first_name = serializers.CharField(source='user.first_name', required=False)
    last_name = serializers.CharField(source='user.last_name', required=False)
    portfolio_images = PortfolioImageSerializer(many=True, read_only=True)
    
    class Meta:
        model = ArtistProfile
        fields = [
            'artist_name', 'slug', 'full_bio', 'short_bio', 'location_city', 'location_state',
            'product_keywords', 'seo_tags', 'categories',
            'etsy_url', 'shopify_url', 'instagram_url', 'tiktok_url', 'website_url', 'contact_email',
            'profile_image', 'banner_image',
            'subscription_plan', 'email', 'first_name', 'last_name', 'rating', 'is_featured', 'is_visible',
            'portfolio_images'
        ]
        read_only_fields = ['subscription_plan', 'email']

    def update(self, instance, validated_data):
        # Handle User fields
        user_data = {}
        if 'user' in validated_data:
            user_data = validated_data.pop('user')
            user = instance.user
            if 'first_name' in user_data:
                user.first_name = user_data['first_name']
            if 'last_name' in user_data:
                user.last_name = user_data['last_name']
            user.save()

        # Categories are expected to be a list
        if 'categories' in validated_data:
            # Ensure it's a list (though JSONField/ListField usually handles this)
            pass
            
        return super().update(instance, validated_data)


class RatingSerializer(serializers.ModelSerializer):
    explorer_username = serializers.CharField(source='explorer.username', read_only=True)
    
    class Meta:
        model = Rating
        fields = ['id', 'artist', 'explorer', 'explorer_username', 'rating', 'created_at', 'updated_at']
        read_only_fields = ['id', 'explorer', 'created_at', 'updated_at']
