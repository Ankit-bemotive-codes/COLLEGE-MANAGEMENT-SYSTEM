from decimal import Decimal, InvalidOperation

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Avg
from django.shortcuts import get_object_or_404, redirect, render

from accounts.decorators import role_required
from academics.models import StudentProfile, Subject

from .models import Exam, Result


@login_required
@role_required("admin", "teacher")
def exam_list(request):
    exams = Exam.objects.select_related("department").all()
    return render(request, "exams/exam_list.html", {"exams": exams})


@login_required
@role_required("admin", "teacher")
def enter_marks(request, exam_id, subject_id):
    exam = get_object_or_404(Exam, pk=exam_id)
    subject = get_object_or_404(Subject, pk=subject_id, department=exam.department)
    students = exam.department.students.select_related("user").order_by("user__first_name")

    existing = {
        result.student_id: result.marks_obtained
        for result in Result.objects.filter(exam=exam, subject=subject)
    }

    if request.method == "POST":
        for student in students:
            raw_marks = request.POST.get(f"marks_{student.id}", "").strip()
            if raw_marks == "":
                continue
            try:
                marks = Decimal(raw_marks)
            except InvalidOperation:
                messages.error(request, f"Invalid marks for {student}: '{raw_marks}' skipped.")
                continue
            Result.objects.update_or_create(
                exam=exam,
                student=student,
                subject=subject,
                defaults={"marks_obtained": marks},
            )
        messages.success(request, f"Marks saved for {subject} — {exam}.")
        return redirect("exams:enter_marks", exam_id=exam.id, subject_id=subject.id)

    rows = [(student, existing.get(student.id, "")) for student in students]
    return render(
        request,
        "exams/enter_marks.html",
        {"exam": exam, "subject": subject, "rows": rows},
    )


@login_required
@role_required("student")
def my_report_card(request):
    profile = get_object_or_404(StudentProfile, user=request.user)
    exams = Exam.objects.filter(results__student=profile).distinct().order_by("-date")

    report = []
    for exam in exams:
        results = Result.objects.filter(exam=exam, student=profile).select_related("subject")
        avg_pct = results.aggregate(avg=Avg("marks_obtained"))["avg"] or 0
        report.append({"exam": exam, "results": results, "average": round(avg_pct, 1)})

    return render(request, "exams/report_card.html", {"report": report})
