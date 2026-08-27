from django.urls import path

from . import views

app_name = "persone"

urlpatterns = [
    path("portale/", views.portale, name="portale"),
    path("portale/telegram/genera-codice/", views.telegram_genera_codice, name="telegram_genera_codice"),
    path("portale/telegram/scollega/", views.telegram_scollega, name="telegram_scollega"),
    path("portale-proprietario/", views.portale_proprietario, name="portale_proprietario"),
    path("portale/consenso/<str:tipo>/accetta/", views.accetta_consenso, name="accetta_consenso"),
    path("portale/tessera/", views.tessera, name="tessera"),
    path("portale/tessera/qr.png", views.tessera_qr_immagine, name="tessera_qr_immagine"),
    path("verifica-tessera/<str:token>/", views.verifica_tessera, name="verifica_tessera"),
]
