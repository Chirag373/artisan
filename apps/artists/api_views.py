from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import ArtistProfile
from .serializers import ArtistProfileSerializer
from apps.users.serializers import SignupSerializer


class ArtistSignupAPIView(APIView):
    """
    API endpoint for Artist signup.
    Handles the subscription package selection.
    """
    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            
            # Retrieve package from request data (default to basic if missing)
            package = request.data.get('package', 'basic')
            
            # Create the associated ArtistProfile
            # Note: We initialize with empty values for fields collected later in the dashboard
            ArtistProfile.objects.create(
                user=user,
                artist_name=user.username,  # Default to username initially
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
        # Fetch featured artists
        artists = ArtistProfile.objects.filter(is_featured=True)
        
        # If no featured artists, fallback to showing recent ones (limit 6)
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
