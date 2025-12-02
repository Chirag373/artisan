from django.views.generic import View, TemplateView
from django.shortcuts import redirect, render
from django.contrib.auth.models import User
from django.contrib.auth import login
from .services import StripeService
from .models import Subscription
from apps.core.telegram import send_telegram_notification

class PaymentSuccessView(View):
    """
    Handles successful return from Stripe.
    Activates subscription and logs the user in.
    """
    def get(self, request):
        session_id = request.GET.get('session_id')
        if not session_id:
            return redirect('signup')

        try:
            # 1. Verify with Stripe
            session = StripeService.retrieve_session(session_id)
            pending_id = session.client_reference_id
            
            # 2. Get Pending Artist
            # We assume client_reference_id is the PendingArtist ID for new signups
            # Note: For future upgrades of existing users, we'd need to check if user exists first
            from apps.artists.models import PendingArtist, ArtistProfile
            
            try:
                pending_artist = PendingArtist.objects.get(id=pending_id)
                
                # 3. Create User
                user = User(
                    username=pending_artist.username,
                    email=pending_artist.email,
                    is_active=True
                )
                user.password = pending_artist.password # Already hashed
                user.save()
                
                # 4. Create Profile
                ArtistProfile.objects.create(
                    user=user,
                    artist_name=user.username,
                    subscription_plan=pending_artist.package
                )
                
                # 5. Create Subscription
                Subscription.objects.create(
                    user=user,
                    stripe_customer_id=session.customer,
                    stripe_subscription_id=session.subscription,
                    plan_name=pending_artist.package,
                    is_active=True
                )

                # Send Telegram Notification
                try:
                    price_paid = session.amount_total / 100 if session.amount_total else 0
                    user_data = {
                        'user_Id': user.id,
                        'email': user.email,
                        'created_at': user.date_joined.strftime("%Y-%m-%d %H:%M:%S"),
                        'payment_details': {
                            'plan': pending_artist.package,
                            'price_paid': f"${price_paid:.2f}",
                            'stripe_id': session.subscription
                        }
                    }
                    send_telegram_notification(user_data)
                except Exception as e:
                    print(f"Error sending telegram notification: {e}")
                
                # 6. Cleanup
                pending_artist.delete()
                
                return redirect('/login/?payment_success=true')
                
            except PendingArtist.DoesNotExist:
                # Handle case where it might be an existing user (future proofing) or error
                print(f"Pending artist not found for ID: {pending_id}")
                return redirect('signup')

        except Exception as e:
            print(f"Payment verification failed: {e}")
            return redirect('login')

class PaymentCancelView(TemplateView):
    template_name = 'subscriptions/payment_cancel.html'

from django.contrib.auth.mixins import LoginRequiredMixin

class SubscriptionPortalView(LoginRequiredMixin, View):
    """
    Redirects to the Stripe Customer Portal for subscription management.
    """
    def get(self, request):
        portal_url = StripeService.create_portal_session(request.user)
        if portal_url:
            return redirect(portal_url)
        # Fallback if something goes wrong (e.g., no subscription found)
        return redirect('artist_dashboard')
