from django.urls import path

from . import views

app_name = "academics"

urlpatterns = [
    path("departments/", views.department_list, name="department_list"),
    path("departments/<int:department_id>/students/", views.student_roster, name="student_roster"),
    path("departments/<int:department_id>/attendance/", views.mark_attendance, name="mark_attendance"),
    path("my-attendance/", views.my_attendance, name="my_attendance"),
]
