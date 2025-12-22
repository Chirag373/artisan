from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import login
from django.db import transaction
from django.contrib.auth.models import User
from .models import ExplorerProfile
from .otp_service import OTPService
from .serializers import SignupSerializer, CustomTokenObtainPairSerializer, ExplorerProfileSerializer


class ExplorerSignupAPIView(APIView):
    """
    API endpoint for Explorer (general user) signup.
    Initiates the signup process by sending an OTP to the provided email.
    """
    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']
            
            # Check if user exists
            try:
                user = User.objects.get(email=email)
                if user.is_active:
                     return Response({"error": "User with this email already exists."}, status=status.HTTP_400_BAD_REQUEST)
                else:
                    # User exists but inactive, update password if needed
                    user.set_password(password)
                    user.save()
            except User.DoesNotExist:
                # Generate unique username
                base_username = email.split('@')[0]
                username = base_username
                counter = 0
                while User.objects.filter(username=username).exists():
                    counter += 1
                    username = f"{base_username}{counter}"

                # Create inactive user
                user = User.objects.create_user(username=username, email=email, password=password)
                user.is_active = False
                user.save()
                ExplorerProfile.objects.create(user=user)

            # Generate and Send OTP
            otp = OTPService.generate_otp()
            OTPService.store_otp(email, otp)
            sent = OTPService.send_otp_email(email, otp)

            if sent:
                return Response({
                    "message": "OTP sent to email. Please verify to complete signup.",
                    "email": email
                }, status=status.HTTP_200_OK)
            else:
                return Response({"error": "Failed to send OTP email."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ExplorerVerifyOTPAPIView(APIView):
    """
    API endpoint to verify OTP and activate the explorer account.
    """
    def post(self, request):
        email = request.data.get('email')
        otp = request.data.get('otp')
        
        if not email or not otp:
             return Response({"error": "Email and OTP are required."}, status=status.HTTP_400_BAD_REQUEST)

        if OTPService.verify_otp(email, otp):
            try:
                user = User.objects.get(email=email)
                user.is_active = True
                user.save()
                
                # Log the user in
                login(request, user)
                
                # Generate JWT tokens
                refresh = RefreshToken.for_user(user)
                
                return Response({
                    "message": "Account verified successfully. You are now logged in.",
                    "username": user.username,
                    "access": str(refresh.access_token),
                    "refresh": str(refresh),
                    "role": "explorer"
                }, status=status.HTTP_200_OK)
            except User.DoesNotExist:
                 return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({"error": "Invalid or expired OTP."}, status=status.HTTP_400_BAD_REQUEST)


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


class BookmarkToggleAPIView(APIView):
    """
    API endpoint to toggle bookmark status for an artist.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, slug):
        from apps.artists.models import ArtistProfile
        from .models import Bookmark

        # Check if user is an explorer
        if not hasattr(request.user, 'explorer_profile'):
            return Response({"error": "Only explorers can bookmark artists"}, status=status.HTTP_403_FORBIDDEN)

        try:
            artist = ArtistProfile.objects.get(slug=slug)
        except ArtistProfile.DoesNotExist:
            return Response({"error": "Artist not found"}, status=status.HTTP_404_NOT_FOUND)

        # Toggle bookmark
        bookmark, created = Bookmark.objects.get_or_create(
            explorer=request.user,
            artist=artist
        )

        if not created:
            # Bookmark already existed, so remove it
            bookmark.delete()
            return Response({
                "message": "Bookmark removed",
                "is_bookmarked": False
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                "message": "Artist bookmarked",
                "is_bookmarked": True
            }, status=status.HTTP_201_CREATED)


class BookmarksListAPIView(APIView):
    """
    API endpoint to retrieve all bookmarked artists for the current explorer.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        from apps.artists.models import ArtistProfile
        from apps.artists.serializers import ArtistProfileSerializer
        from .models import Bookmark

        # Check if user is an explorer
        if not hasattr(request.user, 'explorer_profile'):
            return Response({"error": "Only explorers can view bookmarks"}, status=status.HTTP_403_FORBIDDEN)

        # Get all bookmarked artists
        bookmarks = Bookmark.objects.filter(explorer=request.user).select_related('artist__user')
        artist_ids = bookmarks.values_list('artist_id', flat=True)
        artists = ArtistProfile.objects.filter(id__in=artist_ids, is_visible=True)

        serializer = ArtistProfileSerializer(artists, many=True, context={'request': request})

        return Response({
            'results': serializer.data,
            'count': len(serializer.data)
        })


class CheckBookmarkAPIView(APIView):
    """
    API endpoint to check if the current user has bookmarked a specific artist.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, slug):
        from apps.artists.models import ArtistProfile
        from .models import Bookmark

        # Return False if not an explorer
        if not hasattr(request.user, 'explorer_profile'):
            return Response({"is_bookmarked": False}, status=status.HTTP_200_OK)

        try:
            artist = ArtistProfile.objects.get(slug=slug)
            is_bookmarked = Bookmark.objects.filter(explorer=request.user, artist=artist).exists()
            return Response({"is_bookmarked": is_bookmarked}, status=status.HTTP_200_OK)
        except ArtistProfile.DoesNotExist:
            return Response({"error": "Artist not found"}, status=status.HTTP_404_NOT_FOUND)
