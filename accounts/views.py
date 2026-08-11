from django.contrib import messages
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .decorators import role_required
from .forms import AdminUserCreationForm


class CollegeLoginView(auth_views.LoginView):
    template_name = "accounts/login.html"


class CollegeLogoutView(auth_views.LogoutView):
    next_page = "accounts:login"


@login_required
@role_required("admin")
def create_user(request):
    """Admin-only: create a login account for a new teacher or student."""
    if request.method == "POST":
        form = AdminUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, f"Account created for {user.username} ({user.get_role_display()}).")
            return redirect("accounts:create_user")
    else:
        form = AdminUserCreationForm()

    return render(request, "accounts/create_user.html", {"form": form})
