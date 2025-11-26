from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import login
from django.db import transaction
from .models import ExplorerProfile
from .serializers import SignupSerializer, CustomTokenObtainPairSerializer, ExplorerProfileSerializer


class ExplorerSignupAPIView(APIView):
    """
    API endpoint for Explorer (general user) signup.
    """
    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        if serializer.is_valid():
            # Wrap in transaction to prevent zombie users
            with transaction.atomic():
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
