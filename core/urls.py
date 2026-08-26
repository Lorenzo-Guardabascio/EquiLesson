from django.contrib.auth import views as auth_views
from django.urls import path

from . import views
from .forms import BootstrapAuthenticationForm

app_name = "core"

urlpatterns = [
    path("", views.home, name="home"),
    path(
        "accedi/",
        auth_views.LoginView.as_view(
            template_name="core/login.html",
            authentication_form=BootstrapAuthenticationForm,
        ),
        name="login",
    ),
    path(
        "esci/",
        auth_views.LogoutView.as_view(next_page="core:home"),
        name="logout",
    ),
]
