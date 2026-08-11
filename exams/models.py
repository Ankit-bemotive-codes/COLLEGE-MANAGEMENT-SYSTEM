from django.db import models

from academics.models import Department, StudentProfile, Subject


class Exam(models.Model):
    name = models.CharField(max_length=100, help_text="e.g. 'Mid-Semester 2025', 'End-Semester 2025'")
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name="exams")
    semester = models.PositiveSmallIntegerField(default=1)
    date = models.DateField()

    class Meta:
        ordering = ["-date"]

    def __str__(self):
        return f"{self.name} — {self.department} (Sem {self.semester})"


class Result(models.Model):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name="results")
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name="results")
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name="results")
    marks_obtained = models.DecimalField(max_digits=5, decimal_places=2)
    max_marks = models.DecimalField(max_digits=5, decimal_places=2, default=100)

    class Meta:
        unique_together = ("exam", "student", "subject")

    @property
    def percentage(self):
        if not self.max_marks:
            return 0
        return round((self.marks_obtained / self.max_marks) * 100, 1)

    @property
    def grade(self):
        pct = self.percentage
        if pct >= 90:
            return "A+"
        if pct >= 80:
            return "A"
        if pct >= 70:
            return "B"
        if pct >= 60:
            return "C"
        if pct >= 50:
            return "D"
        return "F"

    def __str__(self):
        return f"{self.student} — {self.subject} — {self.marks_obtained}/{self.max_marks}"
