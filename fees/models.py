import uuid

from django.db import models

from academics.models import Department, StudentProfile


class FeeStructure(models.Model):
    """The fee amount due per term for a given department, e.g. CSE / Semester 3 = ₹45,000."""

    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name="fee_structures")
    semester = models.PositiveSmallIntegerField(default=1)
    term = models.CharField(max_length=50, help_text="e.g. 'Semester 3 2025', 'Annual 2025'")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    due_date = models.DateField()

    class Meta:
        unique_together = ("department", "semester", "term")
        ordering = ["-due_date"]

    def __str__(self):
        return f"{self.department.code} — {self.term} — ₹{self.amount}"


class FeeInvoice(models.Model):
    """
    A specific student's bill for a specific FeeStructure. Generated in bulk
    for every student in a department (see: fees/management/commands/generate_invoices.py),
    then paid individually via Razorpay.
    """

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        PAID = "paid", "Paid"
        OVERDUE = "overdue", "Overdue"

    invoice_number = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name="invoices")
    fee_structure = models.ForeignKey(FeeStructure, on_delete=models.CASCADE, related_name="invoices")
    amount_due = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("student", "fee_structure")
        ordering = ["-created_at"]

    def __str__(self):
        return f"Invoice {self.invoice_number} — {self.student} — ₹{self.amount_due} ({self.get_status_display()})"


class Payment(models.Model):
    """
    One payment attempt/record against an invoice. Created in 'created'
    state when the Razorpay order is opened, then updated to 'success' or
    'failed' once Razorpay confirms — either via the redirect handler or,
    more reliably, via the webhook.
    """

    class Status(models.TextChoices):
        CREATED = "created", "Created"
        SUCCESS = "success", "Success"
        FAILED = "failed", "Failed"

    invoice = models.ForeignKey(FeeInvoice, on_delete=models.CASCADE, related_name="payments")
    razorpay_order_id = models.CharField(max_length=100, unique=True)
    razorpay_payment_id = models.CharField(max_length=100, blank=True)
    razorpay_signature = models.CharField(max_length=255, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.CREATED)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Payment {self.razorpay_order_id} — {self.get_status_display()}"
