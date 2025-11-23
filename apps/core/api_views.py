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


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

from rest_framework.permissions import IsAuthenticated
from .serializers import ExplorerProfileSerializer

class ExplorerProfileDetailView(APIView):
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
