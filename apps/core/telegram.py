import requests
from django.conf import settings

def send_telegram_notification(user_data):
    """
    Sends a notification to Telegram when a new account is created.
    user_data: dict containing user_Id, email, created_at, payment_details
    """
    token = settings.TELEGRAM_BOT_TOKEN
    # Try to get chat_id from settings
    chat_id = getattr(settings, 'TELEGRAM_CHAT_ID', None)
    
    if not chat_id:
        print("TELEGRAM_CHAT_ID not found in settings. Skipping Telegram notification.")
        return

    message = (
        f"New Account Created!\n\n"
        f"User ID: {user_data.get('user_Id')}\n"
        f"Email: {user_data.get('email')}\n"
        f"Created At: {user_data.get('created_at')}\n\n"
        f"Payment Details:\n"
        f"Plan: {user_data.get('payment_details', {}).get('plan')}\n"
        f"Price Paid: {user_data.get('payment_details', {}).get('price_paid')}\n"
        f"Stripe ID: {user_data.get('payment_details', {}).get('stripe_id')}"
    )

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message
    }

    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        print("Telegram notification sent successfully.")
    except Exception as e:
        print(f"Failed to send Telegram notification: {e}")
