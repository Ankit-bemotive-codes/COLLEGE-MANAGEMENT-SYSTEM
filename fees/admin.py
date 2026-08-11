from django.contrib import admin

from .models import FeeInvoice, FeeStructure, Payment


@admin.register(FeeStructure)
class FeeStructureAdmin(admin.ModelAdmin):
    list_display = ("department", "semester", "term", "amount", "due_date")
    list_filter = ("department", "semester")


@admin.register(FeeInvoice)
class FeeInvoiceAdmin(admin.ModelAdmin):
    list_display = ("invoice_number", "student", "fee_structure", "amount_due", "status", "created_at")
    list_filter = ("status", "fee_structure")
    search_fields = ("student__user__first_name", "student__user__last_name", "invoice_number")


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("razorpay_order_id", "invoice", "amount", "status", "created_at")
    list_filter = ("status",)
    readonly_fields = ("razorpay_order_id", "razorpay_payment_id", "razorpay_signature")
