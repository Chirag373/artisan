import stripe
from django.conf import settings

stripe.api_key = settings.STRIPE_SECRET_KEY

class StripeService:
    @staticmethod
    def create_checkout_session(user, plan_name):
        """
        Creates a Stripe Checkout Session for a new subscription.
        """
        # Pricing Map (In cents)
        prices = {
            'basic': 2900,   # $29.00
            'express': 5900, # $59.00
            'premium': 9900  # $99.00
        }
        
        amount = prices.get(plan_name.lower(), 2900)
        
        # Where to go after Stripe
        success_url = f"{settings.BASE_URL}/subscriptions/success/?session_id={{CHECKOUT_SESSION_ID}}"
        cancel_url = f"{settings.BASE_URL}/signup/?package={plan_name}&error=payment_cancelled"

        try:
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                allow_promotion_codes=True,
                line_items=[{
                    'price_data': {
                        'currency': 'usd',
                        'unit_amount': amount,
                        'recurring': {
                            'interval': 'month',
                        },
                        'product_data': {
                            'name': f"ArtisansHub {plan_name.title()} Plan",
                            'description': f"Monthly subscription for {plan_name.title()} access",
                        },
                    },
                    'quantity': 1,
                }],
                mode='subscription',
                success_url=success_url,
                cancel_url=cancel_url,
                client_reference_id=str(user.id),
                customer_email=user.email,
                metadata={
                    'user_id': user.id,
                    'plan_name': plan_name
                }
            )
            return checkout_session.url
        except Exception as e:
            print(f"Stripe Error: {e}")
            raise e

    @staticmethod
    def retrieve_session(session_id):
        return stripe.checkout.Session.retrieve(session_id)

    @staticmethod
    def create_portal_session(user):
        """
        Creates a Stripe Customer Portal session for subscription management.
        """
        try:
            # Get the subscription for the user to find the customer ID
            from .models import Subscription
            subscription = Subscription.objects.get(user=user)
            
            if not subscription.stripe_customer_id:
                raise ValueError("No Stripe customer ID found for user")

            portal_session = stripe.billing_portal.Session.create(
                customer=subscription.stripe_customer_id,
                return_url=f"{settings.BASE_URL}/artist/dashboard/",
            )
            return portal_session.url
        except Exception as e:
            print(f"Stripe Portal Error: {e}")
            return None
