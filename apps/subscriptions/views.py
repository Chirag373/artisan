from django.views.generic import TemplateView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from django.conf import settings
from django.shortcuts import redirect
from .services import StripeService
from apps.artists.models import ArtistProfile
import stripe

class BasicPlanSignupView(TemplateView):
    template_name = 'signup_basic.html'

class BasicPlanCheckoutAPIView(APIView):
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        
        if not email or not password:
            return Response({'error': 'Email and password are required'}, status=status.HTTP_400_BAD_REQUEST)
            
        if User.objects.filter(email=email).exists():
            return Response({'email': ['User with this email already exists.']}, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            # Create inactive user
            user = User.objects.create_user(username=email, email=email, password=password)
            user.is_active = False 
            user.save()
            
            # Create Stripe Session
            stripe_service = StripeService()
            # Construct absolute URLs
            # Note: request.build_absolute_uri might return http in dev, which Stripe accepts for test mode.
            success_url = request.build_absolute_uri('/subscriptions/success/') + '?session_id={CHECKOUT_SESSION_ID}'
            cancel_url = request.build_absolute_uri('/subscriptions/cancel/')
            
            checkout_url = stripe_service.create_checkout_session(
                user=user,
                plan_name='Basic Plan',
                amount=1000, # $10.00
                success_url=success_url,
                cancel_url=cancel_url
            )
            
            if checkout_url:
                return Response({'checkout_url': checkout_url}, status=status.HTTP_200_OK)
            else:
                user.delete()
                return Response({'error': 'Failed to create payment session'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
        except Exception as e:
            # If user was created but session failed, delete user
            if 'user' in locals() and user.pk:
                user.delete()
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class PaymentSuccessView(TemplateView):
    template_name = 'login.html'
    
    def get(self, request, *args, **kwargs):
        session_id = request.GET.get('session_id')
        if session_id:
            stripe.api_key = settings.STRIPE_SECRET_KEY
            try:
                session = stripe.checkout.Session.retrieve(session_id)
                if session.payment_status == 'paid':
                    user_id = session.client_reference_id
                    try:
                        user = User.objects.get(id=user_id)
                        if not user.is_active:
                            user.is_active = True
                            user.save()
                            
                            # Create Artist Profile
                            if not hasattr(user, 'artist_profile'):
                                ArtistProfile.objects.create(
                                    user=user,
                                    artist_name=user.email.split('@')[0], # Default name
                                    subscription_plan='basic'
                                )
                            
                            # Save Subscription Info
                            from .models import Subscription
                            Subscription.objects.create(
                                user=user,
                                stripe_customer_id=session.customer,
                                stripe_subscription_id=session.subscription,
                                plan_name='basic'
                            )
                    except User.DoesNotExist:
                        pass
            except Exception as e:
                print(f"Error processing success: {e}")
                pass
        
        return redirect('login')

class PaymentCancelView(TemplateView):
    template_name = 'signup_basic.html'

class CustomerPortalView(APIView):
    def get(self, request):
        if not request.user.is_authenticated:
            return redirect('login')
            
        try:
            from .models import Subscription
            subscription = Subscription.objects.get(user=request.user)
            
            if not subscription.stripe_customer_id:
                return redirect('artist_dashboard') # Or show error
                
            stripe_service = StripeService()
            # Return to dashboard after portal
            return_url = request.build_absolute_uri('/artists/dashboard/')
            
            portal_url = stripe_service.create_customer_portal_session(
                customer_id=subscription.stripe_customer_id,
                return_url=return_url
            )
            
            if portal_url:
                return redirect(portal_url)
            else:
                return redirect('artist_dashboard') # Or show error
                
        except Subscription.DoesNotExist:
            # If no subscription, maybe redirect to join page?
            return redirect('join_artist')
        except Exception as e:
            print(f"Error accessing portal: {e}")
            return redirect('artist_dashboard')
