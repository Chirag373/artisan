from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from .models import ExplorerProfile


class SignupSerializer(serializers.ModelSerializer):
    password_confirm = serializers.CharField(write_only=True)
    
    package = serializers.CharField(required=False, write_only=True)

    class Meta:
        model = User
        fields = ('email', 'password', 'password_confirm', 'package')
        extra_kwargs = {
            'email': {'required': True},
            'password': {'write_only': True}
        }

    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError({"password": "Passwords do not match."})
        
        validate_password(data['password'])
        
        if User.objects.filter(email=data['email']).exists():
            raise serializers.ValidationError({"email": "This email is already in use."})
            
        return data

    def create(self, validated_data):
        from django.db import IntegrityError
        
        validated_data.pop('password_confirm', None)
        package = validated_data.pop('package', None)
        
        email = validated_data['email']
        base_username = email.split('@')[0]
        
        # Fix race condition: retry on IntegrityError
        max_attempts = 10
        for attempt in range(max_attempts):
            username = base_username if attempt == 0 else f"{base_username}{attempt}"
            
            try:
                user = User.objects.create_user(
                    username=username,
                    email=validated_data['email'],
                    password=validated_data['password']
                )
                return user
            except IntegrityError:
                # Username was taken between check and create, try next one
                if attempt == max_attempts - 1:
                    raise serializers.ValidationError({
                        "username": "Unable to generate unique username. Please try again."
                    })
                continue


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    username_field = 'username'
    
    def validate(self, attrs):
        username_or_email = attrs.get(self.username_field)
        
        if '@' in username_or_email:
            try:
                user = User.objects.get(email=username_or_email)
                attrs[self.username_field] = user.username
            except User.DoesNotExist:
                pass
        
        data = super().validate(attrs)
        
        role = 'unknown'
        if hasattr(self.user, 'artist_profile'):
            role = 'artist'
        elif hasattr(self.user, 'explorer_profile'):
            role = 'explorer'
            
        data['role'] = role
        data['username'] = self.user.username
        
        return data


class ExplorerProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)
    first_name = serializers.CharField(source='user.first_name', required=False)
    last_name = serializers.CharField(source='user.last_name', required=False)
    
    class Meta:
        model = ExplorerProfile
        fields = ['username', 'email', 'first_name', 'last_name', 'phone_number', 
                  'street_number', 'street_address', 'city', 'state', 
                  'zip_code', 'promotion_keywords']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        required_fields = ['first_name', 'last_name', 'phone_number', 'street_number', 'street_address', 'city', 'state', 'zip_code']
        missing_fields = [field for field in required_fields if not data.get(field)]
        data['is_complete'] = len(missing_fields) == 0
        data['missing_fields'] = missing_fields
        return data

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', {})
        user = instance.user
        
        if 'first_name' in user_data and not user.first_name:
            user.first_name = user_data['first_name']
        
        if 'last_name' in user_data and not user.last_name:
            user.last_name = user_data['last_name']
            
        if user_data:
            user.save()
            
        return super().update(instance, validated_data)
