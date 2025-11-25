import stripe
from django.conf import settings

class StripeService:
    def __init__(self):
        stripe.api_key = settings.STRIPE_SECRET_KEY

    def create_checkout_session(self, user, plan_name='Basic Plan', amount=999, currency='usd', success_url=None, cancel_url=None):
        """
        Creates a Stripe Checkout Session for a subscription.
        """
        try:
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[
                    {
                        'price_data': {
                            'currency': currency,
                            'product_data': {
                                'name': plan_name,
                            },
                            'unit_amount': amount,
                            'recurring': {
                                'interval': 'month',
                            },
                        },
                        'quantity': 1,
                    },
                ],
                mode='subscription',
                success_url=success_url,
                cancel_url=cancel_url,
                customer_email=user.email,
                client_reference_id=str(user.id),
                metadata={
                    'user_id': str(user.id),
                    'plan': plan_name,
                }
            )
            return checkout_session.url
        except Exception as e:
            print(f"Error creating Stripe session: {e}")
            return None

    def create_customer_portal_session(self, customer_id, return_url):
        """
        Creates a Stripe Customer Portal session.
        """
        try:
            session = stripe.billing_portal.Session.create(
                customer=customer_id,
                return_url=return_url,
            )
            return session.url
        except Exception as e:
            print(f"Error creating portal session: {e}")
            return None
