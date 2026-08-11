from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class CollegeUserAdmin(UserAdmin):
    list_display = ("username", "first_name", "last_name", "role", "email", "is_active")
    list_filter = ("role", "is_active")
    fieldsets = UserAdmin.fieldsets + (
        ("College role", {"fields": ("role", "phone_number")}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ("College role", {"fields": ("role", "phone_number")}),
    )
