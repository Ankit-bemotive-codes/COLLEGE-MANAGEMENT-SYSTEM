from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render

from accounts.decorators import role_required
from accounts.models import User
from academics.models import Attendance, Department, StudentProfile
from fees.models import FeeInvoice


@login_required
def redirect_to_dashboard(request):
    """Single entry point after login — sends each role to its own dashboard."""
    role = request.user.role
    if role == User.Role.ADMIN:
        return redirect("dashboard:admin")
    if role == User.Role.TEACHER:
        return redirect("dashboard:teacher")
    return redirect("dashboard:student")


@login_required
@role_required("admin")
def admin_dashboard(request):
    total_students = StudentProfile.objects.count()
    total_departments = Department.objects.count()

    invoice_counts = FeeInvoice.objects.aggregate(
        total=Count("id"),
        paid=Count("id", filter=Q(status=FeeInvoice.Status.PAID)),
    )
    collection_rate = (
        round((invoice_counts["paid"] / invoice_counts["total"]) * 100, 1) if invoice_counts["total"] else 0
    )

    context = {
        "total_students": total_students,
        "total_departments": total_departments,
        "total_invoices": invoice_counts["total"],
        "paid_invoices": invoice_counts["paid"],
        "collection_rate": collection_rate,
    }
    return render(request, "dashboard/admin_dashboard.html", context)


@login_required
@role_required("teacher")
def teacher_dashboard(request):
    profile = getattr(request.user, "teacher_profile", None)
    headed_departments = Department.objects.filter(head_of_department=profile) if profile else Department.objects.none()
    own_department = profile.department if profile else None
    return render(
        request,
        "dashboard/teacher_dashboard.html",
        {"headed_departments": headed_departments, "own_department": own_department},
    )


@login_required
@role_required("student")
def student_dashboard(request):
    profile = get_object_or_404(StudentProfile, user=request.user)

    records = profile.attendance_records.all()
    total = records.count()
    present = records.filter(status=Attendance.Status.PRESENT).count()
    attendance_pct = round((present / total) * 100, 1) if total else 0

    pending_invoices = profile.invoices.exclude(status=FeeInvoice.Status.PAID)

    context = {
        "profile": profile,
        "attendance_pct": attendance_pct,
        "pending_invoices": pending_invoices,
        "pending_count": pending_invoices.count(),
    }
    return render(request, "dashboard/student_dashboard.html", context)
