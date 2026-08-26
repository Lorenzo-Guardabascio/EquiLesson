from django.urls import path

from . import views

app_name = "lezioni"

urlpatterns = [
    path("calendario/", views.calendario, name="calendario"),
    path("calendario/eventi.json", views.eventi_json, name="eventi_json"),
]
