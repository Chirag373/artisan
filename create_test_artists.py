#!/usr/bin/env python
"""Script to create test artists for infinite scroll testing"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'artisanshub.settings')
django.setup()

from django.contrib.auth.models import User
from apps.artists.models import ArtistProfile
import random

# Sample data
artist_names = [
    "Creative Canvas", "Artisan Alley", "Pixel Perfect", "Crafty Corner",
    "Design Dreams", "Maker's Mark", "Studio Spark", "Artistic Visions",
    "Handmade Haven", "Creative Collective", "Art & Soul", "Craft Masters",
    "Design District", "Maker Space", "Creative Hub", "Artisan Works",
    "Studio Seven", "Craft Central", "Design Lab", "Creative Corner"
]

cities = ["New York", "Los Angeles", "Chicago", "Houston", "Phoenix", "Philadelphia", 
          "San Antonio", "San Diego", "Dallas", "San Jose", "Austin", "Jacksonville",
          "Fort Worth", "Columbus", "Charlotte", "San Francisco", "Indianapolis", "Seattle"]

states = ["NY", "CA", "IL", "TX", "AZ", "PA", "TX", "CA", "TX", "CA", "TX", "FL",
          "TX", "OH", "NC", "CA", "IN", "WA"]

categories_list = [
    ["stickers", "prints"],
    ["fan_art", "posters"],
    ["keychains", "pins"],
    ["t-shirts", "mugs"],
    ["prints", "posters"],
    ["stickers", "keychains", "pins"],
]

bios = [
    "Creating unique handmade items with love and care. Each piece tells a story.",
    "Passionate about bringing art to life through various mediums and styles.",
    "Specializing in custom designs that capture your imagination and personality.",
    "Transforming ideas into beautiful, tangible creations for over 5 years.",
    "Dedicated to crafting high-quality, one-of-a-kind pieces for art lovers.",
]

# Create artists
created_count = 0
for i, name in enumerate(artist_names):
    username = f"artist_{i+10}"
    
    # Check if user already exists
    if User.objects.filter(username=username).exists():
        print(f"User {username} already exists, skipping...")
        continue
    
    # Create user
    user = User.objects.create_user(
        username=username,
        email=f"{username}@example.com",
        password="testpass123"
    )
    
    # Create artist profile
    artist = ArtistProfile.objects.create(
        user=user,
        artist_name=name,
        full_bio=random.choice(bios),
        location_city=cities[i % len(cities)],
        location_state=states[i % len(states)],
        categories=random.choice(categories_list),
        subscription_plan=random.choice(['basic', 'express', 'premium']),
        is_featured=random.choice([True, False, False]),  # 33% chance of being featured
        rating=None
    )
    
    created_count += 1
    print(f"Created artist: {name} (@{username})")

print(f"\nTotal artists created: {created_count}")
print(f"Total artists in database: {ArtistProfile.objects.count()}")
print(f"Featured artists: {ArtistProfile.objects.filter(is_featured=True).count()}")
