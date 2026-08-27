from django.contrib.auth import views as auth_views
from django.urls import path

from . import gestione, views
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
    path("gestione/<slug:slug>/", gestione.gestione_lista, name="gestione_lista"),
    path("gestione/<slug:slug>/nuovo/", gestione.gestione_form, name="gestione_nuovo"),
    path("gestione/<slug:slug>/<int:pk>/modifica/", gestione.gestione_form, name="gestione_modifica"),
    path("gestione/<slug:slug>/<int:pk>/elimina/", gestione.gestione_elimina, name="gestione_elimina"),
    path("impostazioni/", views.impostazioni_form, name="impostazioni"),
]
