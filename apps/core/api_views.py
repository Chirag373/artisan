# apps/core/api_views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import SignupSerializer
from .models import ExplorerProfile, ArtistProfile
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import CustomTokenObtainPairSerializer

class ExplorerSignupAPIView(APIView):
    """
    API endpoint for Explorer (general user) signup.
    """
    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            
            # Create the associated ExplorerProfile
            ExplorerProfile.objects.create(user=user)
            
            return Response({
                "message": "Explorer account created successfully",
                "username": user.username
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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


from django.contrib.auth import login

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        # We need to validate first to get the user
        serializer = self.get_serializer(data=request.data)
        
        try:
            serializer.is_valid(raise_exception=True)
        except Exception:
            # If validation fails, let the parent class handle the response generation
            return super().post(request, *args, **kwargs)
            
        # If valid, log the user in to the Django session
        # This is crucial for hybrid apps that use both API tokens and Django templates/sessions
        login(request, serializer.user)
        
        # Return the standard token response
        return Response(serializer.validated_data, status=status.HTTP_200_OK)

from rest_framework.permissions import IsAuthenticated
from .serializers import ExplorerProfileSerializer

class ExplorerProfileDetailView(APIView):
    """
    API endpoint for the Explorer Profile Detail.
    Allows authenticated explorers to retrieve and update their profile data.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            profile = request.user.explorer_profile
            serializer = ExplorerProfileSerializer(profile)
            return Response(serializer.data)
        except ExplorerProfile.DoesNotExist:
            return Response({"error": "Profile not found"}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request):
        try:
            profile = request.user.explorer_profile
            serializer = ExplorerProfileSerializer(profile, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except ExplorerProfile.DoesNotExist:
            return Response({"error": "Profile not found"}, status=status.HTTP_404_NOT_FOUND)

from .serializers import ArtistProfileSerializer

class ArtistDashboardAPIView(APIView):
    """
    API endpoint for the Artist Dashboard.
    Allows authenticated artists to retrieve and update their profile data.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            profile = request.user.artist_profile
            serializer = ArtistProfileSerializer(profile)
            return Response(serializer.data)
        except ArtistProfile.DoesNotExist:
            return Response({"error": "Artist profile not found"}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request):
        try:
            profile = request.user.artist_profile
            serializer = ArtistProfileSerializer(profile, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except ArtistProfile.DoesNotExist:
            return Response({"error": "Artist profile not found"}, status=status.HTTP_404_NOT_FOUND)

from rest_framework.permissions import AllowAny

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
            
        serializer = ArtistProfileSerializer(artists, many=True)
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
            serializer = ArtistProfileSerializer(profile)
            return Response(serializer.data)
        except ArtistProfile.DoesNotExist:
            return Response({"error": "Artist not found"}, status=status.HTTP_404_NOT_FOUND)
