from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models


class CollegeUserManager(UserManager):
    use_in_migrations = True

    def create_superuser(self, username, email=None, password=None, **extra_fields):
        extra_fields["role"] = "admin"
        return super().create_superuser(username, email, password, **extra_fields)


class User(AbstractUser):
    """
    Custom user model. Every account (admin staff, teacher, or student)
    logs in through this single model, distinguished by `role`.

    Keeping role on the User itself (rather than only inferring it from
    a related Teacher/Student row) makes permission checks cheap and
    lets us use it directly in templates: {% if user.role == 'teacher' %}.
    """

    class Role(models.TextChoices):
        ADMIN = "admin", "Admin"
        TEACHER = "teacher", "Teacher"
        STUDENT = "student", "Student"

    role = models.CharField(max_length=10, choices=Role.choices, default=Role.STUDENT)
    phone_number = models.CharField(max_length=20, blank=True)
    objects = CollegeUserManager()

    @property
    def is_admin_role(self):
        return self.role == self.Role.ADMIN

    @property
    def is_teacher(self):
        return self.role == self.Role.TEACHER

    @property
    def is_student(self):
        return self.role == self.Role.STUDENT

    def __str__(self):
        display_name = (self.get_full_name() or self.username or "User").strip()
        if self.role in self.Role.values:
            role_label = self.Role(self.role).label
        else:
            role_label = self.role or "Unknown"
        return f"{display_name} ({role_label})"
