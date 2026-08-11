from django.contrib import admin

from .models import Attendance, Department, StudentProfile, Subject, TeacherProfile


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "head_of_department")


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "department", "semester", "teacher")
    list_filter = ("department", "semester")


@admin.register(TeacherProfile)
class TeacherProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "employee_id", "department", "joining_date")
    list_filter = ("department",)
    search_fields = ("user__username", "user__first_name", "user__last_name", "employee_id")


@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "admission_number", "department", "semester")
    list_filter = ("department", "semester")
    search_fields = ("user__username", "user__first_name", "user__last_name", "admission_number")


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ("student", "date", "status", "marked_by")
    list_filter = ("status", "date")
