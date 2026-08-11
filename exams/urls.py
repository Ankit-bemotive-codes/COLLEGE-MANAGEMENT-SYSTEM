from django.urls import path

from . import views

app_name = "exams"

urlpatterns = [
    path("", views.exam_list, name="exam_list"),
    path("<int:exam_id>/subjects/<int:subject_id>/marks/", views.enter_marks, name="enter_marks"),
    path("my-report-card/", views.my_report_card, name="report_card"),
]
