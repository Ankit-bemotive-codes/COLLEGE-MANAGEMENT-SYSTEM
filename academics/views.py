from datetime import date

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from accounts.decorators import role_required

from .models import Attendance, Department, StudentProfile


@login_required
@role_required("admin", "teacher")
def department_list(request):
    departments = Department.objects.select_related("head_of_department").all()
    return render(request, "academics/department_list.html", {"departments": departments})


@login_required
@role_required("admin", "teacher")
def student_roster(request, department_id):
    department = get_object_or_404(Department, pk=department_id)
    students = department.students.select_related("user").order_by("semester", "user__first_name")
    return render(request, "academics/student_roster.html", {"department": department, "students": students})


@login_required
@role_required("admin", "teacher")
def mark_attendance(request, department_id):
    """
    Simple one-page-per-day attendance sheet: teacher checks each student
    present/absent/late and submits once for the whole department.
    """
    department = get_object_or_404(Department, pk=department_id)
    students = department.students.select_related("user").order_by("user__first_name")
    today = date.today()

    existing = {
        record.student_id: record.status
        for record in Attendance.objects.filter(student__department=department, date=today)
    }

    if request.method == "POST":
        for student in students:
            status = request.POST.get(f"status_{student.id}", Attendance.Status.PRESENT)
            Attendance.objects.update_or_create(
                student=student,
                date=today,
                defaults={"status": status, "marked_by": request.user},
            )
        messages.success(request, f"Attendance saved for {department} on {today}.")
        return redirect("academics:mark_attendance", department_id=department.id)

    rows = [(student, existing.get(student.id, Attendance.Status.PRESENT)) for student in students]
    return render(
        request,
        "academics/mark_attendance.html",
        {"department": department, "rows": rows, "today": today, "status_choices": Attendance.Status.choices},
    )


@login_required
@role_required("student")
def my_attendance(request):
    profile = get_object_or_404(StudentProfile, user=request.user)
    records = profile.attendance_records.all()
    total = records.count()
    present = records.filter(status=Attendance.Status.PRESENT).count()
    percentage = round((present / total) * 100, 1) if total else 0
    return render(
        request,
        "academics/my_attendance.html",
        {"records": records, "percentage": percentage, "total": total, "present": present},
    )
