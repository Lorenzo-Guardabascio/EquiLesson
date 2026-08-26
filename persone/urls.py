from django.urls import path

from . import views

app_name = "persone"

urlpatterns = [
    path("portale/", views.portale, name="portale"),
]
