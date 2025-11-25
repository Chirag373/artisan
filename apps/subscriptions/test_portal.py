from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from apps.subscriptions.models import Subscription
from unittest.mock import patch, MagicMock

class CustomerPortalTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.portal_url = reverse('customer_portal')
        self.user = User.objects.create_user(username='portaluser', password='password')
        self.client.force_login(self.user)

    def test_redirect_to_join_if_no_subscription(self):
        """
        If the user has no subscription record, they should be redirected to the join page.
        """
        response = self.client.get(self.portal_url)
        self.assertRedirects(response, reverse('join_artist'))

    @patch('apps.subscriptions.views.StripeService.create_customer_portal_session')
    def test_redirect_to_portal_if_subscription_exists(self, mock_create_portal):
        """
        If the user has a subscription, they should be redirected to the Stripe portal.
        """
        # Create subscription
        Subscription.objects.create(
            user=self.user,
            stripe_customer_id='cus_test123',
            stripe_subscription_id='sub_test123'
        )
        
        mock_create_portal.return_value = 'https://billing.stripe.com/test-session'
        
        response = self.client.get(self.portal_url)
        self.assertRedirects(response, 'https://billing.stripe.com/test-session', fetch_redirect_response=False)

    def test_redirect_to_login_if_unauthenticated(self):
        self.client.logout()
        response = self.client.get(self.portal_url)
        self.assertRedirects(response, reverse('login'))
