from django.urls import path

from . import views

app_name = "dashboard"

urlpatterns = [
    path("", views.redirect_to_dashboard, name="redirect"),
    path("admin-dashboard/", views.admin_dashboard, name="admin"),
    path("teacher-dashboard/", views.teacher_dashboard, name="teacher"),
    path("student-dashboard/", views.student_dashboard, name="student"),
]
