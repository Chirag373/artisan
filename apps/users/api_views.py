from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import login
from .models import ExplorerProfile
from .serializers import SignupSerializer, CustomTokenObtainPairSerializer, ExplorerProfileSerializer


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
