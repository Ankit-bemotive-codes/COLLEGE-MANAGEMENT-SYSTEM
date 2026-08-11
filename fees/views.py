import razorpay
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.csrf import csrf_exempt

from accounts.decorators import role_required
from academics.models import StudentProfile

from . import gateway
from .emails import send_payment_receipt_email
from .models import FeeInvoice, Payment


@login_required
@role_required("student")
def invoice_list(request):
    profile = get_object_or_404(StudentProfile, user=request.user)
    invoices = profile.invoices.select_related("fee_structure").all()
    return render(request, "fees/invoice_list.html", {"invoices": invoices})


@login_required
@role_required("student")
def pay_invoice(request, invoice_id):
    """
    Creates a Razorpay order for this invoice and renders Razorpay's
    Checkout.js modal. The actual "did the money arrive" confirmation
    happens in payment_success (redirect) AND razorpay_webhook (server to
    server) — the webhook is the source of truth, the redirect is just UX.
    """
    invoice = get_object_or_404(FeeInvoice, pk=invoice_id, student__user=request.user)

    if invoice.status == FeeInvoice.Status.PAID:
        messages.info(request, "This invoice is already paid.")
        return redirect("fees:invoice_list")

    order = gateway.create_order(invoice.amount_due, receipt=str(invoice.invoice_number))

    Payment.objects.update_or_create(
        invoice=invoice,
        razorpay_order_id=order["id"],
        defaults={"amount": invoice.amount_due, "status": Payment.Status.CREATED},
    )

    context = {
        "invoice": invoice,
        "order_id": order["id"],
        "amount_paise": order["amount"],
        "razorpay_key_id": settings.RAZORPAY_KEY_ID,
        "student_name": request.user.get_full_name() or request.user.username,
        "student_email": request.user.email,
    }
    return render(request, "fees/pay.html", context)


@login_required
@role_required("student")
def payment_success(request):
    """
    Razorpay Checkout.js posts back here after the user completes payment.
    We verify the signature before trusting anything — this is what stops
    someone from faking a "payment succeeded" request.
    """
    order_id = request.POST.get("razorpay_order_id")
    payment_id = request.POST.get("razorpay_payment_id")
    signature = request.POST.get("razorpay_signature")

    payment = get_object_or_404(Payment, razorpay_order_id=order_id, invoice__student__user=request.user)

    try:
        gateway.verify_payment_signature(
            {
                "razorpay_order_id": order_id,
                "razorpay_payment_id": payment_id,
                "razorpay_signature": signature,
            }
        )
    except razorpay.errors.SignatureVerificationError:
        payment.status = Payment.Status.FAILED
        payment.save(update_fields=["status"])
        messages.error(request, "Payment verification failed. Please contact the office if money was deducted.")
        return redirect("fees:payment_failed")

    payment.razorpay_payment_id = payment_id
    payment.razorpay_signature = signature
    payment.status = Payment.Status.SUCCESS
    payment.save(update_fields=["razorpay_payment_id", "razorpay_signature", "status"])

    invoice = payment.invoice
    invoice.status = FeeInvoice.Status.PAID
    invoice.save(update_fields=["status"])

    send_payment_receipt_email(payment)

    return render(request, "fees/order_success.html", {"payment": payment, "invoice": invoice})


@login_required
def payment_failed(request):
    return render(request, "fees/order_cancel.html")


@csrf_exempt
def razorpay_webhook(request):
    """
    Server-to-server confirmation from Razorpay. This is the *reliable*
    path — the browser redirect above can be interrupted (closed tab,
    network drop) but the webhook will still fire, so this is what
    actually keeps invoice status correct.
    """
    if request.method != "POST":
        return _webhook_response(405)

    payload_body = request.body
    signature = request.headers.get("X-Razorpay-Signature", "")

    try:
        gateway.verify_webhook_signature(payload_body, signature)
    except razorpay.errors.SignatureVerificationError:
        return _webhook_response(400)

    import json

    event = json.loads(payload_body)
    event_type = event.get("event")

    if event_type == "payment.captured":
        payload = event["payload"]["payment"]["entity"]
        order_id = payload.get("order_id")
        payment_id = payload.get("id")

        try:
            payment = Payment.objects.select_related("invoice").get(razorpay_order_id=order_id)
        except Payment.DoesNotExist:
            return _webhook_response(200)  # nothing to do, but acknowledge receipt

        if payment.status != Payment.Status.SUCCESS:
            payment.razorpay_payment_id = payment_id
            payment.status = Payment.Status.SUCCESS
            payment.save(update_fields=["razorpay_payment_id", "status"])

            invoice = payment.invoice
            if invoice.status != FeeInvoice.Status.PAID:
                invoice.status = FeeInvoice.Status.PAID
                invoice.save(update_fields=["status"])
                send_payment_receipt_email(payment)

    elif event_type == "payment.failed":
        payload = event["payload"]["payment"]["entity"]
        order_id = payload.get("order_id")
        Payment.objects.filter(razorpay_order_id=order_id).update(status=Payment.Status.FAILED)

    return _webhook_response(200)


def _webhook_response(status_code):
    from django.http import HttpResponse

    return HttpResponse(status=status_code)


@login_required
@role_required("student")
def receipt(request, payment_id):
    payment = get_object_or_404(Payment, pk=payment_id, invoice__student__user=request.user, status=Payment.Status.SUCCESS)
    return render(request, "fees/receipt.html", {"payment": payment})
