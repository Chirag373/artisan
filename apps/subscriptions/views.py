from django.views.generic import View, TemplateView
from django.shortcuts import redirect, render
from django.contrib.auth.models import User
from django.contrib.auth import login
from .services import StripeService
from .models import Subscription

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
            # 1. Verify with Stripe (Double-check)
            session = StripeService.retrieve_session(session_id)
            user_id = session.client_reference_id
            
            # 2. Get the User
            user = User.objects.get(id=user_id)
            plan_name = session.metadata.get('plan_name', 'basic')
            
            # 3. Activate Subscription locally
            subscription, _ = Subscription.objects.get_or_create(user=user)
            subscription.stripe_customer_id = session.customer
            subscription.stripe_subscription_id = session.subscription
            subscription.plan_name = plan_name
            subscription.is_active = True
            subscription.save()
            
            # 4. Update Profile metadata if needed
            if hasattr(user, 'artist_profile'):
                user.artist_profile.subscription_plan = plan_name
                user.artist_profile.save()
            
            # 5. Log them in (Bypassing password check since they just paid)
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            
            # 6. Show Success Page
            return render(request, 'subscriptions/payment_success.html', {
                'plan_name': plan_name
            })
            
        except Exception as e:
            print(f"Payment verification failed: {e}")
            return redirect('login')

class PaymentCancelView(TemplateView):
    template_name = 'subscriptions/payment_cancel.html'
