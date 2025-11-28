import random
import string
from django.core.cache import cache
from django.core.mail import send_mail
from django.conf import settings

class OTPService:
    @staticmethod
    def generate_otp(length=8):
        return ''.join(random.choices(string.digits, k=length))

    @staticmethod
    def store_otp(email, otp, timeout=300): # 5 minutes
        cache.set(f'otp_{email}', otp, timeout)

    @staticmethod
    def verify_otp(email, otp):
        stored_otp = cache.get(f'otp_{email}')
        if stored_otp and str(stored_otp) == str(otp):
            cache.delete(f'otp_{email}')
            return True
        return False

    @staticmethod
    def send_otp_email(email, otp):
        subject = 'Verify your email address - ArtistaHub'
        message = f'Your verification code is: {otp}\n\nPlease enter this code to verify your account.'
        from_email = settings.DEFAULT_FROM_EMAIL
        recipient_list = [email]
        try:
            send_mail(subject, message, from_email, recipient_list)
            return True
        except Exception as e:
            print(f"Error sending email: {e}")
            return False
