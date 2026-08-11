from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import User


class AdminUserCreationForm(UserCreationForm):
    """
    Used by admins to create teacher/student login accounts.
    (Public self-registration is intentionally not exposed — in a real
    college system, accounts are provisioned by the office, not signed
    up for by anyone off the street.)
    """

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ["username", "first_name", "last_name", "email", "role", "phone_number"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault("class", "form-control")
