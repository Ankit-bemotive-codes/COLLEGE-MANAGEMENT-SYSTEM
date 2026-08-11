from functools import wraps

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect


def role_required(*allowed_roles):
    """
    Restrict a view to users whose `role` is in `allowed_roles`.

    Usage:
        @role_required("admin")
        def add_student(request): ...

        @role_required("admin", "teacher")
        def mark_attendance(request): ...
    """

    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def _wrapped(request, *args, **kwargs):
            if request.user.role not in allowed_roles:
                messages.error(request, "You don't have permission to view that page.")
                return redirect("dashboard:redirect")
            return view_func(request, *args, **kwargs)

        return _wrapped

    return decorator
