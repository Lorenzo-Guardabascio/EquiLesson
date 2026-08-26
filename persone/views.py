import secrets
from datetime import timedelta

from django.conf import settings
from django.contrib import messages
from django.shortcuts import redirect, render
from django.utils import timezone

from comunicazioni.models import TelegramLink
from core.models import Impostazioni
from lezioni.models import Partecipazione
from pacchetti.models import Pacchetto

from .decorators import allievo_required


def _genera_codice_telegram():
    return secrets.token_hex(4)  # 8 caratteri esadecimali, comodi da ricopiare a mano


@allievo_required
def portale(request):
    """Portale di sola lettura per allievi/genitori: proprie lezioni + pacchetto residuo."""
    allievo = request.user.allievo
    oggi = timezone.localdate()

    partecipazioni_future = (
        Partecipazione.objects.filter(allievo=allievo, lezione__data__gte=oggi)
        .exclude(stato=Partecipazione.Stato.ANNULLATA)
        .select_related("lezione", "lezione__tipo_lezione", "lezione__istruttore", "lezione__campo", "cavallo")
        .order_by("lezione__data", "lezione__ora_inizio")
    )
    partecipazioni_passate = (
        Partecipazione.objects.filter(allievo=allievo, lezione__data__lt=oggi)
        .select_related("lezione", "lezione__tipo_lezione", "lezione__istruttore", "lezione__campo", "cavallo")
        .order_by("-lezione__data", "-lezione__ora_inizio")[:10]
    )

    pacchetti = allievo.pacchetti.select_related("tipo_pacchetto").order_by("-data_inizio")
    pacchetto_attivo = pacchetti.filter(stato=Pacchetto.Stato.ATTIVO).first()

    limite_scadenza = oggi + timedelta(days=30)
    scadenze = []
    if allievo.certificato_medico_scadenza:
        scadenze.append({
            "etichetta": "Certificato medico",
            "scadenza": allievo.certificato_medico_scadenza,
            "urgente": allievo.certificato_medico_scadenza <= limite_scadenza,
        })
    if allievo.tessera_fise_scadenza:
        scadenze.append({
            "etichetta": "Tessera FISE",
            "scadenza": allievo.tessera_fise_scadenza,
            "urgente": allievo.tessera_fise_scadenza <= limite_scadenza,
        })
    if allievo.tessera_fitetrek_scadenza:
        scadenze.append({
            "etichetta": "Tessera FITETREK",
            "scadenza": allievo.tessera_fitetrek_scadenza,
            "urgente": allievo.tessera_fitetrek_scadenza <= limite_scadenza,
        })

    telegram_link = TelegramLink.objects.filter(allievo=allievo).first()

    return render(request, "persone/portale.html", {
        "allievo": allievo,
        "partecipazioni_future": partecipazioni_future,
        "partecipazioni_passate": partecipazioni_passate,
        "pacchetto_attivo": pacchetto_attivo,
        "pacchetti": pacchetti,
        "scadenze": scadenze,
        "prenotazione_autonoma_abilitata": Impostazioni.get().prenotazione_autonoma_abilitata,
        "telegram_abilitato": Impostazioni.get().notifiche_telegram_abilitate,
        "telegram_link": telegram_link,
        "telegram_bot_username": settings.TELEGRAM_BOT_USERNAME,
    })


@allievo_required
def telegram_genera_codice(request):
    if request.method != "POST":
        return redirect("persone:portale")
    allievo = request.user.allievo
    link, _ = TelegramLink.objects.get_or_create(allievo=allievo)
    if not link.collegato:
        link.codice_collegamento = _genera_codice_telegram()
        link.save(update_fields=["codice_collegamento"])
        messages.success(request, "Codice generato: invialo al bot Telegram come indicato qui sotto.")
    return redirect("persone:portale")


@allievo_required
def telegram_scollega(request):
    if request.method != "POST":
        return redirect("persone:portale")
    TelegramLink.objects.filter(allievo=request.user.allievo).update(
        chat_id="", codice_collegamento="", collegato_il=None
    )
    messages.success(request, "Telegram scollegato.")
    return redirect("persone:portale")
