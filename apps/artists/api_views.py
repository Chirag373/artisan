from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import ArtistProfile
from .serializers import ArtistProfileSerializer
from apps.users.serializers import SignupSerializer
from django.db.models import Q


class ArtistSignupAPIView(APIView):
    """
    API endpoint for Artist signup.
    Handles the subscription package selection.
    """
    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            
            package = request.data.get('package', 'basic')
            
            ArtistProfile.objects.create(
                user=user,
                artist_name=user.username,
                subscription_plan=package
            )
            
            return Response({
                "message": "Artist account created successfully",
                "username": user.username,
                "package": package
            }, status=status.HTTP_201_CREATED)
            
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ArtistDashboardAPIView(APIView):
    """
    API endpoint for the Artist Dashboard.
    Allows authenticated artists to retrieve and update their profile data.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            profile = request.user.artist_profile
            serializer = ArtistProfileSerializer(profile, context={'request': request})
            return Response(serializer.data)
        except ArtistProfile.DoesNotExist:
            return Response({"error": "Artist profile not found"}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request):
        try:
            profile = request.user.artist_profile
            serializer = ArtistProfileSerializer(profile, data=request.data, partial=True, context={'request': request})
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except ArtistProfile.DoesNotExist:
            return Response({"error": "Artist profile not found"}, status=status.HTTP_404_NOT_FOUND)


class FeaturedArtistsAPIView(APIView):
    """
    API endpoint to retrieve featured artists for the homepage.
    Returns a list of artists marked as featured.
    """
    permission_classes = [AllowAny]

    def get(self, request):
        query = request.query_params.get('q')
        location = request.query_params.get('location')
        
        if query or location:
            artists = ArtistProfile.objects.all()
            
            if query:
                artists = artists.filter(
                    Q(artist_name__icontains=query) |
                    Q(full_bio__icontains=query) |
                    Q(product_keywords__icontains=query) |
                    Q(seo_tags__icontains=query) |
                    Q(categories__icontains=query)
                )
            
            if location:
                artists = artists.filter(
                    Q(location_city__icontains=location) |
                    Q(location_state__icontains=location)
                )
            
            # If search yields results, order by rating or relevance (here just rating/created_at)
            artists = artists.order_by('-rating', '-created_at')
        else:
            # Default behavior: show featured artists
            artists = ArtistProfile.objects.filter(is_featured=True)
            
            # Fallback if no featured artists
            if not artists.exists():
                artists = ArtistProfile.objects.all().order_by('-created_at')[:6]
            
        serializer = ArtistProfileSerializer(artists, many=True, context={'request': request})
        return Response(serializer.data)


class ArtistProfileDetailAPIView(APIView):
    """
    API endpoint to retrieve a single artist profile by slug.
    Publicly accessible.
    """
    permission_classes = [AllowAny]

    def get(self, request, slug):
        try:
            profile = ArtistProfile.objects.get(slug=slug)
            serializer = ArtistProfileSerializer(profile, context={'request': request})
            return Response(serializer.data)
        except ArtistProfile.DoesNotExist:
            return Response({"error": "Artist not found"}, status=status.HTTP_404_NOT_FOUND)


class RateArtistAPIView(APIView):
    """
    API endpoint for explorers to rate artists.
    Only authenticated explorers can rate.
    Artists cannot rate other artists.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, slug):
        try:
            artist_profile = ArtistProfile.objects.get(slug=slug)
        except ArtistProfile.DoesNotExist:
            return Response({"error": "Artist not found"}, status=status.HTTP_404_NOT_FOUND)

        # Check if user is an artist (artists cannot rate)
        if hasattr(request.user, 'artist_profile'):
            return Response({
                "error": "Artists cannot rate other artists"
            }, status=status.HTTP_403_FORBIDDEN)

        # Check if user is an explorer
        if not hasattr(request.user, 'explorer_profile'):
            return Response({
                "error": "Only explorers can rate artists"
            }, status=status.HTTP_403_FORBIDDEN)

        rating_value = request.data.get('rating')
        
        if not rating_value:
            return Response({"error": "Rating value is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            rating_value = int(rating_value)
            if rating_value < 1 or rating_value > 5:
                return Response({"error": "Rating must be between 1 and 5"}, status=status.HTTP_400_BAD_REQUEST)
        except (ValueError, TypeError):
            return Response({"error": "Invalid rating value"}, status=status.HTTP_400_BAD_REQUEST)

        # Create or update rating
        from .models import Rating
        rating, created = Rating.objects.update_or_create(
            artist=artist_profile,
            explorer=request.user,
            defaults={'rating': rating_value}
        )

        # Update artist's average rating
        from django.db.models import Avg
        avg_rating = Rating.objects.filter(artist=artist_profile).aggregate(Avg('rating'))['rating__avg']
        artist_profile.rating = round(avg_rating, 1) if avg_rating else None
        artist_profile.save()

        from .serializers import RatingSerializer
        serializer = RatingSerializer(rating)
        
        return Response({
            "message": "Rating submitted successfully" if created else "Rating updated successfully",
            "rating": serializer.data,
            "average_rating": float(artist_profile.rating) if artist_profile.rating else None
        }, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)

    def get(self, request, slug):
        """Get the current user's rating for this artist"""
        if not request.user.is_authenticated:
            return Response({"error": "Authentication required"}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            artist_profile = ArtistProfile.objects.get(slug=slug)
        except ArtistProfile.DoesNotExist:
            return Response({"error": "Artist not found"}, status=status.HTTP_404_NOT_FOUND)

        from .models import Rating
        try:
            rating = Rating.objects.get(artist=artist_profile, explorer=request.user)
            from .serializers import RatingSerializer
            serializer = RatingSerializer(rating)
            return Response(serializer.data)
        except Rating.DoesNotExist:
            return Response({"rating": None}, status=status.HTTP_200_OK)
