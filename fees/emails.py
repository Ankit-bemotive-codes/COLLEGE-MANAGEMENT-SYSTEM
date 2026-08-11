from django.core.mail import send_mail


def send_payment_receipt_email(payment):
    """Fire-and-forget confirmation email. Swallows errors so a flaky SMTP
    server never breaks the payment flow itself — the invoice is already
    marked paid at this point regardless of whether the email sends."""
    student_user = payment.invoice.student.user
    if not student_user.email:
        return

    subject = f"Payment received — Invoice {payment.invoice.invoice_number}"
    message = (
        f"Hi {student_user.get_full_name() or student_user.username},\n\n"
        f"We've received your payment of ₹{payment.amount} for "
        f"{payment.invoice.fee_structure}.\n\n"
        f"Payment ID: {payment.razorpay_payment_id}\n"
        f"Invoice: {payment.invoice.invoice_number}\n\n"
        "Thank you.\nCollege Office"
    )
    try:
        send_mail(subject, message, None, [student_user.email], fail_silently=True)
    except Exception:
        # Never let an email failure break the payment flow.
        pass
