import io
import secrets
from datetime import timedelta

import qrcode
from django.conf import settings
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.core import signing
from django.core.signing import BadSignature
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone

from comunicazioni.models import TelegramLink
from core.models import Impostazioni
from lezioni.models import Partecipazione
from pacchetti.models import Pacchetto

from .consensi_testi import TESTO_FOTO_VIDEO, TESTO_PRIVACY
from .decorators import allievo_required, proprietario_required
from .models import Allievo, ConsensoLog

TESSERA_SALT = "persone.tessera-digitale"

TESTI_CONSENSO = {
    ConsensoLog.Tipo.PRIVACY: TESTO_PRIVACY,
    ConsensoLog.Tipo.FOTO_VIDEO: TESTO_FOTO_VIDEO,
}


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

    consensi = [
        {
            "tipo": ConsensoLog.Tipo.PRIVACY,
            "etichetta": ConsensoLog.Tipo.PRIVACY.label,
            "testo": TESTO_PRIVACY,
            "dato": allievo.consenso_privacy,
            "ultimo": allievo.consensi.filter(tipo=ConsensoLog.Tipo.PRIVACY).first(),
        },
        {
            "tipo": ConsensoLog.Tipo.FOTO_VIDEO,
            "etichetta": ConsensoLog.Tipo.FOTO_VIDEO.label,
            "testo": TESTO_FOTO_VIDEO,
            "dato": allievo.consenso_foto_video,
            "ultimo": allievo.consensi.filter(tipo=ConsensoLog.Tipo.FOTO_VIDEO).first(),
        },
    ]

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
        "consensi": consensi,
    })


@allievo_required
def accetta_consenso(request, tipo):
    if request.method != "POST" or tipo not in TESTI_CONSENSO:
        return redirect("persone:portale")

    allievo = request.user.allievo
    testo = TESTI_CONSENSO[tipo]
    ConsensoLog.objects.create(
        allievo=allievo,
        tipo=tipo,
        indirizzo_ip=request.META.get("REMOTE_ADDR"),
        testo_accettato=testo,
    )
    campo_booleano = "consenso_privacy" if tipo == ConsensoLog.Tipo.PRIVACY else "consenso_foto_video"
    setattr(allievo, campo_booleano, True)
    allievo.save(update_fields=[campo_booleano])

    messages.success(request, "Consenso registrato.")
    return redirect("persone:portale")


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


@proprietario_required
def portale_proprietario(request):
    """Portale di sola lettura per i proprietari di cavalli in pensione:
    stato dei propri cavalli e prossime scadenze sanitarie."""
    proprietario = request.user.proprietario
    oggi = timezone.localdate()
    limite_scadenza = oggi + timedelta(days=30)

    cavalli = list(proprietario.cavalli.prefetch_related("scadenze_sanitarie").order_by("nome"))
    for cavallo in cavalli:
        # attributo attaccato qui invece che con un dict a parte: il template
        # può leggerlo come un campo qualsiasi, senza bisogno di un filtro
        # custom per il lookup su dizionario.
        cavallo.scadenze_ordinate = [
            {"scadenza": s, "urgente": s.data_scadenza <= limite_scadenza}
            for s in sorted(cavallo.scadenze_sanitarie.all(), key=lambda s: s.data_scadenza)
        ]

    return render(request, "persone/portale_proprietario.html", {
        "proprietario": proprietario,
        "cavalli": cavalli,
    })


def _token_tessera(allievo):
    return signing.dumps(allievo.pk, salt=TESSERA_SALT)


@allievo_required
def tessera(request):
    """Tessera digitale con QR: la card si vede nel portale, il QR incorpora
    l'URL di verifica che apre lo staff (non l'allievo stesso)."""
    allievo = request.user.allievo
    url_verifica = request.build_absolute_uri(
        reverse("persone:verifica_tessera", args=[_token_tessera(allievo)])
    )
    return render(request, "persone/tessera.html", {"allievo": allievo, "url_verifica": url_verifica})


@allievo_required
def tessera_qr_immagine(request):
    """Restituisce il PNG del QR della propria tessera (non quella di un altro:
    il token si genera qui, dall'allievo collegato alla sessione, non da un
    parametro scelto dal chiamante)."""
    allievo = request.user.allievo
    url_verifica = request.build_absolute_uri(
        reverse("persone:verifica_tessera", args=[_token_tessera(allievo)])
    )
    img = qrcode.make(url_verifica)
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    return HttpResponse(buffer.getvalue(), content_type="image/png")


@staff_member_required
def verifica_tessera(request, token):
    """Pagina di verifica che apre lo staff scansionando il QR di un allievo.

    Riservata allo staff (non pubblica): mostra solo dati identificativi e di
    tesseramento, MAI il certificato medico o le note riservate, anche se chi
    scansiona è autorizzato — non c'è motivo di esporli in questo contesto.
    """
    try:
        allievo_id = signing.loads(token, salt=TESSERA_SALT)
    except BadSignature:
        return render(request, "persone/verifica_tessera.html", {"valido": False})

    allievo = get_object_or_404(Allievo, pk=allievo_id)
    return render(request, "persone/verifica_tessera.html", {"valido": True, "allievo": allievo})
