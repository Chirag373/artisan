# Artisan Project

A Django-based platform for artist subscriptions and profiles.

## Setup

### 1. Clone the repository
```bash
git clone https://github.com/Chirag373/artisan.git
cd artisan
```

### 2. Create virtual environment
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the project root with your Stripe API keys:

```
STRIPE_PUBLIC_KEY=your_stripe_publishable_key_here
STRIPE_SECRET_KEY=your_stripe_secret_key_here
```

**To get your Stripe keys:**
1. Go to [Stripe Dashboard](https://dashboard.stripe.com/test/apikeys)
2. Copy your Publishable key and Secret key
3. Paste them into the `.env` file

### 5. Run migrations
```bash
python manage.py migrate
```

### 6. Run the development server
```bash
python manage.py runserver
```

Visit http://127.0.0.1:8000 in your browser.

## Features

- Artist profiles and dashboards
- Subscription management with Stripe
- Stripe Customer Portal integration
- Payment processing

## Important Note

Never commit your `.env` file or expose your Stripe API keys publicly!
