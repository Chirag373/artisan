from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.db.models import Q, Avg
from django.db import transaction
from .models import ArtistProfile, Rating
from .serializers import ArtistProfileSerializer, RatingSerializer
from apps.users.serializers import SignupSerializer


class ArtistSignupAPIView(APIView):
    """
    API endpoint for Artist signup.
    Handles the subscription package selection.
    """
    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        
        # 1. Guard Clause: Return errors immediately if invalid
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            # 2. Atomic Transaction: Ensures both User and Profile are created, or neither.
            with transaction.atomic():
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

        except Exception as e:
            # No need to manually delete user; transaction.atomic handles the rollback
            return Response(
                {"error": f"Failed to create artist profile: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


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
        
        try:
            page = int(request.query_params.get('page', 1))
            page_size = int(request.query_params.get('page_size', 6))
            if page < 1 or page_size < 1:
                raise ValueError
        except (ValueError, TypeError):
            return Response({"error": "Invalid pagination parameters"}, status=status.HTTP_400_BAD_REQUEST)
        
        offset = (page - 1) * page_size
        
        queryset = ArtistProfile.objects.select_related('user')
        
        if query or location:
            if query:
                queryset = queryset.filter(
                    Q(artist_name__icontains=query) |
                    Q(full_bio__icontains=query) |
                    Q(product_keywords__icontains=query) |
                    Q(seo_tags__icontains=query) |
                    Q(categories__icontains=query)
                )
            
            if location:
                queryset = queryset.filter(
                    Q(location_city__icontains=location) |
                    Q(location_state__icontains=location)
                )
            
            queryset = queryset.order_by('-rating', '-created_at')
        else:
            featured_queryset = queryset.filter(is_featured=True)
            
            if featured_queryset.exists():
                queryset = featured_queryset
            else:
                queryset = queryset.order_by('-created_at')
        
        total_count = queryset.count()
        artists = queryset[offset:offset + page_size]
        
        serializer = ArtistProfileSerializer(artists, many=True, context={'request': request})
        
        return Response({
            'results': serializer.data,
            'count': total_count,
            'page': page,
            'page_size': page_size,
            'has_more': offset + page_size < total_count
        })


class ArtistProfileDetailAPIView(APIView):
    """
    API endpoint to retrieve a single artist profile by slug.
    Publicly accessible.
    """
    permission_classes = [AllowAny]

    def get(self, request, slug):
        try:
            # Fix N+1 query problem with select_related
            profile = ArtistProfile.objects.select_related('user').get(slug=slug)
            serializer = ArtistProfileSerializer(profile, context={'request': request})
            return Response(serializer.data)
        except ArtistProfile.DoesNotExist:
            return Response({"error": "Artist not found"}, status=status.HTTP_404_NOT_FOUND)


class RateArtistAPIView(APIView):
    """
    API endpoint for explorers to rate artists.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, slug):
        try:
            artist_profile = ArtistProfile.objects.get(slug=slug)
        except ArtistProfile.DoesNotExist:
            return Response({"error": "Artist not found"}, status=status.HTTP_404_NOT_FOUND)

        # 1. Role Checks (Kept manual as per your specific business logic requirements)
        if hasattr(request.user, 'artist_profile'):
            return Response({"error": "Artists cannot rate other artists"}, status=status.HTTP_403_FORBIDDEN)

        if not hasattr(request.user, 'explorer_profile'):
            return Response({"error": "Only explorers can rate artists"}, status=status.HTTP_403_FORBIDDEN)

        # 2. Use Serializer for Validation (Pattern Match)
        # We pass data={'rating': ...} to validate just that field against model rules
        validation_serializer = RatingSerializer(data=request.data, partial=True)
        if not validation_serializer.is_valid():
            return Response(validation_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        validated_rating = validation_serializer.validated_data['rating']

        # 3. Create or Update Logic
        rating, created = Rating.objects.update_or_create(
            artist=artist_profile,
            explorer=request.user,
            defaults={'rating': validated_rating}
        )

        # 4. Update Aggregates (With your race condition fix)
        avg_rating = Rating.objects.filter(artist=artist_profile).aggregate(Avg('rating'))['rating__avg']
        artist_profile.rating = round(avg_rating, 1) if avg_rating else None
        artist_profile.save(update_fields=['rating'])

        # 5. Return Response
        return Response({
            "message": "Rating submitted successfully" if created else "Rating updated successfully",
            "rating": RatingSerializer(rating).data,
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

        try:
            rating = Rating.objects.get(artist=artist_profile, explorer=request.user)
            return Response(RatingSerializer(rating).data)
        except Rating.DoesNotExist:
            return Response({"rating": None}, status=status.HTTP_200_OK)
