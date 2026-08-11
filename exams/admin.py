from django.contrib import admin

from .models import Exam, Result


@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ("name", "department", "semester", "date")
    list_filter = ("department", "semester")


@admin.register(Result)
class ResultAdmin(admin.ModelAdmin):
    list_display = ("exam", "student", "subject", "marks_obtained", "max_marks")
    list_filter = ("exam", "subject")
    search_fields = ("student__user__first_name", "student__user__last_name")
