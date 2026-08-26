from datetime import timedelta

from django.shortcuts import render
from django.utils import timezone

from core.models import Impostazioni
from lezioni.models import Partecipazione
from pacchetti.models import Pacchetto

from .decorators import allievo_required


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

    return render(request, "persone/portale.html", {
        "allievo": allievo,
        "partecipazioni_future": partecipazioni_future,
        "partecipazioni_passate": partecipazioni_passate,
        "pacchetto_attivo": pacchetto_attivo,
        "pacchetti": pacchetti,
        "scadenze": scadenze,
        "prenotazione_autonoma_abilitata": Impostazioni.get().prenotazione_autonoma_abilitata,
    })
