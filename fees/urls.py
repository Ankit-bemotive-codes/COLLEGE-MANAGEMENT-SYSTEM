from django.urls import path

from . import views

app_name = "fees"

urlpatterns = [
    path("", views.invoice_list, name="invoice_list"),
    path("<int:invoice_id>/pay/", views.pay_invoice, name="pay_invoice"),
    path("payment/success/", views.payment_success, name="payment_success"),
    path("payment/failed/", views.payment_failed, name="payment_failed"),
    path("payment/<int:payment_id>/receipt/", views.receipt, name="receipt"),
    path("webhook/razorpay/", views.razorpay_webhook, name="razorpay_webhook"),
]
