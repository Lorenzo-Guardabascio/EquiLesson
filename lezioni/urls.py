from django.urls import path

from . import views

app_name = "lezioni"

urlpatterns = [
    path("calendario/", views.calendario, name="calendario"),
    path("calendario/eventi.json", views.eventi_json, name="eventi_json"),
    path("nuova/", views.lezione_form, name="lezione_nuova"),
    path("<int:pk>/modifica/", views.lezione_form, name="lezione_modifica"),
    path("<int:pk>/elimina/", views.lezione_elimina, name="lezione_elimina"),
    path("prenota/", views.prenota, name="prenota"),
    path("prenota/<int:pk>/conferma/", views.prenota_conferma, name="prenota_conferma"),
    path("partecipazione/<int:pk>/annulla/", views.annulla_prenotazione, name="annulla_prenotazione"),
]
