from django.urls import path

from . import views

app_name = "comunicazioni"

urlpatterns = [
    path("", views.comunicazione_lista, name="lista"),
    path("nuova/", views.comunicazione_nuova, name="nuova"),
]
