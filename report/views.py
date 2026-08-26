from datetime import date, timedelta

from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Count, Q
from django.shortcuts import render
from django.utils import timezone

from cavalli.models import ScadenzaSanitaria
from lezioni.models import Lezione, Partecipazione
from pacchetti.models import Pacchetto
from persone.models import Allievo

GIORNI_PREAVVISO_SCADENZE = 30


def _periodo(request):
    """Intervallo di date per i report da filtro (default: dal 1° del mese corrente a oggi)."""
    oggi = timezone.localdate()
    default_dal = oggi.replace(day=1)

    dal = request.GET.get("dal")
    al = request.GET.get("al")
    try:
        dal = date.fromisoformat(dal) if dal else default_dal
    except ValueError:
        dal = default_dal
    try:
        al = date.fromisoformat(al) if al else oggi
    except ValueError:
        al = oggi

    return dal, al


def _presenze_per_allievo(dal, al):
    righe = (
        Partecipazione.objects.filter(lezione__data__gte=dal, lezione__data__lte=al)
        .values("allievo__id", "allievo__nome", "allievo__cognome")
        .annotate(
            totale=Count("id"),
            svolte=Count("id", filter=Q(stato=Partecipazione.Stato.SVOLTA)),
            assenti=Count("id", filter=Q(stato=Partecipazione.Stato.ASSENTE)),
        )
        .order_by("allievo__cognome", "allievo__nome")
    )
    risultato = []
    for r in righe:
        presenze_registrate = r["svolte"] + r["assenti"]
        percentuale = round(100 * r["svolte"] / presenze_registrate) if presenze_registrate else None
        risultato.append({**r, "percentuale": percentuale})
    return risultato


def _utilizzo_cavalli(dal, al):
    return list(
        Partecipazione.objects.filter(
            lezione__data__gte=dal, lezione__data__lte=al, cavallo__isnull=False
        )
        .values("cavallo__id", "cavallo__nome")
        .annotate(numero_lezioni=Count("id"))
        .order_by("-numero_lezioni")
    )


def _occupazione_istruttori(dal, al):
    return list(
        Lezione.objects.filter(data__gte=dal, data__lte=al, istruttore__isnull=False)
        .values("istruttore__id", "istruttore__nome", "istruttore__cognome")
        .annotate(numero_lezioni=Count("id"))
        .order_by("-numero_lezioni")
    )


def _occupazione_campi(dal, al):
    return list(
        Lezione.objects.filter(data__gte=dal, data__lte=al, campo__isnull=False)
        .values("campo__id", "campo__nome")
        .annotate(numero_lezioni=Count("id"))
        .order_by("-numero_lezioni")
    )


def _allievi_in_scadenza(oggi):
    limite = oggi + timedelta(days=GIORNI_PREAVVISO_SCADENZE)
    voci = []

    campi_scadenza = [
        ("certificato_medico_scadenza", "Certificato medico"),
        ("tessera_fise_scadenza", "Tessera FISE"),
        ("tessera_fitetrek_scadenza", "Tessera FITETREK"),
    ]
    allievi_attivi = Allievo.objects.filter(stato=Allievo.Stato.ATTIVO)
    for campo, etichetta in campi_scadenza:
        filtro = {f"{campo}__isnull": False, f"{campo}__lte": limite}
        for allievo in allievi_attivi.filter(**filtro):
            scadenza = getattr(allievo, campo)
            voci.append({
                "allievo": allievo, "tipo": etichetta, "scadenza": scadenza, "scaduto": scadenza < oggi,
            })

    for pacchetto in Pacchetto.objects.filter(
        stato=Pacchetto.Stato.ATTIVO, data_scadenza__lte=limite
    ).select_related("allievo", "tipo_pacchetto"):
        voci.append({
            "allievo": pacchetto.allievo,
            "tipo": f"Pacchetto ({pacchetto.tipo_pacchetto.nome}, {pacchetto.lezioni_residue} residue)",
            "scadenza": pacchetto.data_scadenza,
            "scaduto": pacchetto.data_scadenza < oggi,
        })

    voci.sort(key=lambda v: v["scadenza"])
    return voci


def _cavalli_in_scadenza(oggi):
    limite = oggi + timedelta(days=GIORNI_PREAVVISO_SCADENZE)
    voci = []
    for scadenza in ScadenzaSanitaria.objects.filter(data_scadenza__lte=limite).select_related("cavallo"):
        voci.append({
            "cavallo": scadenza.cavallo,
            "tipo": scadenza.get_tipo_display(),
            "scadenza": scadenza.data_scadenza,
            "scaduto": scadenza.data_scadenza < oggi,
        })
    voci.sort(key=lambda v: v["scadenza"])
    return voci


@staff_member_required
def report(request):
    dal, al = _periodo(request)
    oggi = timezone.localdate()

    return render(request, "report/report.html", {
        "dal": dal,
        "al": al,
        "presenze": _presenze_per_allievo(dal, al),
        "utilizzo_cavalli": _utilizzo_cavalli(dal, al),
        "occupazione_istruttori": _occupazione_istruttori(dal, al),
        "occupazione_campi": _occupazione_campi(dal, al),
        "scadenze": _allievi_in_scadenza(oggi),
        "scadenze_cavalli": _cavalli_in_scadenza(oggi),
    })
