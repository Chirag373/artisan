from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q, Avg
from django.db import transaction
from .models import ArtistProfile, Rating, PortfolioImage
from .serializers import ArtistProfileSerializer, RatingSerializer
from apps.users.serializers import SignupSerializer
from apps.subscriptions.services import StripeService
from apps.users.otp_service import OTPService
from django.contrib.auth.models import User
from django.contrib.auth import login


class ArtistSignupAPIView(APIView):
    """
    API endpoint for Artist signup.
    Handles the subscription package selection and initiates OTP verification.
    """
    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        
        # 1. Guard Clause: Return errors immediately if invalid
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']
            package = request.data.get('package', 'basic')

            # 2. Check if user exists
            try:
                user = User.objects.get(email=email)
                if user.is_active:
                     return Response({"error": "User with this email already exists."}, status=status.HTTP_400_BAD_REQUEST)
                else:
                    # User exists but inactive, update password if needed
                    user.set_password(password)
                    user.save()
                    # Update or create profile if it doesn't exist
                    ArtistProfile.objects.update_or_create(
                        user=user,
                        defaults={'subscription_plan': package, 'artist_name': user.username}
                    )
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
                
                ArtistProfile.objects.create(
                    user=user,
                    artist_name=user.username,
                    subscription_plan=package
                )

            # 3. Generate and Send OTP
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

        except Exception as e:
            return Response(
                {"error": f"Failed to create artist profile: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ArtistVerifyOTPAPIView(APIView):
    """
    API endpoint to verify OTP, activate the artist account, and generate Stripe session.
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
                
                # Get profile and create Stripe session
                profile = user.artist_profile
                checkout_url = StripeService.create_checkout_session(user, profile.subscription_plan)
                
                return Response({
                    "message": "Account verified successfully.",
                    "username": user.username,
                    "checkout_url": checkout_url
                }, status=status.HTTP_200_OK)
            except User.DoesNotExist:
                 return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)
            except Exception as e:
                return Response({"error": f"Error during activation: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response({"error": "Invalid or expired OTP."}, status=status.HTTP_400_BAD_REQUEST)


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
        
        queryset = ArtistProfile.objects.filter(is_visible=True).select_related('user')
        
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
            # Order by is_featured (True first) then created_at (newest first)
            queryset = queryset.order_by('-is_featured', '-created_at')
        
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


class PortfolioUploadAPIView(APIView):
    """
    API endpoint for uploading portfolio images.
    Handles bulk uploads and enforces plan limits.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            artist_profile = request.user.artist_profile
        except (AttributeError, ObjectDoesNotExist):
            return Response({"error": "Artist profile not found"}, status=status.HTTP_404_NOT_FOUND)

        # 1. Check Plan Limits
        plan = artist_profile.subscription_plan
        current_count = artist_profile.portfolio_images.count()
        
        # Define limits
        LIMITS = {
            'basic': 6,
            'express': 6,
            'premium': 50
        }
        
        limit = LIMITS.get(plan, 6)
        
        # 2. Get Files
        images = request.FILES.getlist('images')
        if not images:
            return Response({"error": "No images provided"}, status=status.HTTP_400_BAD_REQUEST)

        if current_count + len(images) > limit:
            return Response({
                "error": f"Upload exceeds plan limit. You can upload {limit - current_count} more images."
            }, status=status.HTTP_400_BAD_REQUEST)

        # 3. Save Images
        created_images = []
        for image in images:
            # Basic validation could go here (size, type)
            portfolio_image = PortfolioImage.objects.create(
                artist=artist_profile,
                image=image
            )
            created_images.append(portfolio_image)

        # 4. Return Response
        from .serializers import PortfolioImageSerializer  # Local import to avoid circular dependency if any
        serializer = PortfolioImageSerializer(created_images, many=True)
        
        return Response({
            "message": f"Successfully uploaded {len(created_images)} images",
            "images": serializer.data
        }, status=status.HTTP_201_CREATED)

    def delete(self, request, image_id):
        """Delete a portfolio image"""
        try:
            artist_profile = request.user.artist_profile
            image = PortfolioImage.objects.get(id=image_id, artist=artist_profile)
            image.delete()
            return Response({"message": "Image deleted successfully"}, status=status.HTTP_200_OK)
        except (PortfolioImage.DoesNotExist, AttributeError):
            return Response({"error": "Image not found"}, status=status.HTTP_404_NOT_FOUND)
