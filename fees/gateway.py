"""
Thin wrapper around the Razorpay SDK.

Kept separate from views.py on purpose: every call that talks to Razorpay's
API goes through here, so if we ever swap payment providers, this is the
only file that changes.
"""
import razorpay
from django.conf import settings


def get_client():
    return razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))


def create_order(amount_rupees, receipt):
    """
    Create a Razorpay order for the given amount (in rupees — Razorpay's
    API wants paise, so we convert here to keep that detail out of views.py).
    """
    client = get_client()
    amount_paise = int(round(float(amount_rupees) * 100))
    order = client.order.create(
        {
            "amount": amount_paise,
            "currency": "INR",
            "receipt": receipt,
            "payment_capture": 1,
        }
    )
    return order


def verify_payment_signature(params):
    """
    params must contain: razorpay_order_id, razorpay_payment_id, razorpay_signature.
    Raises razorpay.errors.SignatureVerificationError if invalid.
    """
    client = get_client()
    client.utility.verify_payment_signature(params)


def verify_webhook_signature(payload_body, signature):
    """
    Verifies the X-Razorpay-Signature header against the raw request body
    using the separate webhook secret (configured in the Razorpay dashboard,
    distinct from the API key secret).
    """
    client = get_client()
    client.utility.verify_webhook_signature(payload_body, signature, settings.RAZORPAY_WEBHOOK_SECRET)
