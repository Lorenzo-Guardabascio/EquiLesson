from datetime import datetime

from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.db import transaction
from django.db.models import Count, F, Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext as _
from django.utils.translation import gettext_lazy as _lazy

from core.decorators import richiede_impostazione
from core.models import Impostazioni
from persone.decorators import allievo_required

from .forms import LezioneForm, PartecipazioneFormSet
from .models import Lezione, Partecipazione

# Colore per stato lezione (esadecimale, usato dal calendario).
COLORE_STATO = {
    Lezione.Stato.PRENOTATA: "#6c757d",   # grigio
    Lezione.Stato.CONFERMATA: "#0d6efd",  # blu
    Lezione.Stato.SVOLTA: "#198754",      # verde
    Lezione.Stato.ANNULLATA: "#dc3545",   # rosso
}


@staff_member_required
def calendario(request):
    return render(request, "lezioni/calendario.html")


@staff_member_required
def eventi_json(request):
    """Restituisce le lezioni nell'intervallo richiesto da FullCalendar (parametri start/end)."""
    inizio = request.GET.get("start")
    fine = request.GET.get("end")

    qs = Lezione.objects.select_related("tipo_lezione", "istruttore", "campo").prefetch_related(
        "partecipazioni__allievo"
    )
    if inizio:
        qs = qs.filter(data__gte=datetime.fromisoformat(inizio).date())
    if fine:
        qs = qs.filter(data__lte=datetime.fromisoformat(fine).date())

    eventi = []
    for lezione in qs:
        allievi = ", ".join(p.allievo.nome for p in lezione.partecipazioni.all()) or "Nessun allievo"
        titolo = f"{lezione.tipo_lezione} - {allievi}"
        eventi.append({
            "id": lezione.id,
            "title": titolo,
            "start": f"{lezione.data}T{lezione.ora_inizio}",
            "end": f"{lezione.data}T{lezione.ora_fine}",
            "color": COLORE_STATO.get(lezione.stato, "#6c757d"),
            "url": reverse("lezioni:lezione_modifica", args=[lezione.id]),
            "extendedProps": {
                "campo": str(lezione.campo) if lezione.campo else "",
                "istruttore": str(lezione.istruttore) if lezione.istruttore else "",
                "stato": lezione.get_stato_display(),
            },
        })
    return JsonResponse(eventi, safe=False)


@staff_member_required
def lezione_form(request, pk=None):
    lezione = get_object_or_404(Lezione, pk=pk) if pk else None
    titolo = "Modifica lezione" if lezione else "Nuova lezione"

    if request.method == "POST":
        form = LezioneForm(request.POST, instance=lezione)
        with transaction.atomic():
            if form.is_valid():
                lezione_obj = form.save()
                formset = PartecipazioneFormSet(request.POST, instance=lezione_obj)
                if formset.is_valid():
                    formset.save()
                    messages.success(request, _("Lezione salvata correttamente."))
                    return redirect("lezioni:calendario")
                transaction.set_rollback(True)
            else:
                formset = PartecipazioneFormSet(request.POST, instance=lezione or Lezione())
    else:
        form = LezioneForm(instance=lezione)
        formset = PartecipazioneFormSet(instance=lezione)

    return render(request, "lezioni/lezione_form.html", {
        "form": form, "formset": formset, "lezione": lezione, "titolo": titolo,
    })


@staff_member_required
def lezione_elimina(request, pk):
    lezione = get_object_or_404(Lezione, pk=pk)
    if request.method == "POST":
        lezione.delete()
        messages.success(request, _("Lezione eliminata."))
        return redirect("lezioni:calendario")
    return render(request, "lezioni/lezione_conferma_elimina.html", {"lezione": lezione})


def _prenotazione_autonoma_attiva():
    return Impostazioni.get().prenotazione_autonoma_abilitata


_MESSAGGIO_FEATURE_DISATTIVA = _lazy("La prenotazione autonoma non è attiva al momento: contatta la segreteria.")


@allievo_required
@richiede_impostazione(_prenotazione_autonoma_attiva, "persone:portale", _MESSAGGIO_FEATURE_DISATTIVA)
def prenota(request):
    """Elenco delle lezioni future aperte alla prenotazione autonoma (posti liberi, non già proprie)."""
    allievo = request.user.allievo
    oggi = timezone.localdate()

    lezioni_aperte = (
        Lezione.objects.filter(data__gte=oggi)
        .exclude(stato=Lezione.Stato.ANNULLATA)
        .exclude(
            Q(partecipazioni__allievo=allievo)
            & ~Q(partecipazioni__stato=Partecipazione.Stato.ANNULLATA)
        )
        .annotate(
            n_partecipanti=Count(
                "partecipazioni",
                filter=~Q(partecipazioni__stato=Partecipazione.Stato.ANNULLATA),
            )
        )
        .filter(
            Q(tipo_lezione__capienza_max__isnull=True)
            | Q(n_partecipanti__lt=F("tipo_lezione__capienza_max"))
        )
        .select_related("tipo_lezione", "istruttore", "campo")
        .order_by("data", "ora_inizio")
        .distinct()
    )

    return render(request, "lezioni/prenota.html", {"lezioni_aperte": lezioni_aperte})


@allievo_required
@richiede_impostazione(_prenotazione_autonoma_attiva, "persone:portale", _MESSAGGIO_FEATURE_DISATTIVA)
def prenota_conferma(request, pk):
    if request.method != "POST":
        return redirect("lezioni:prenota")

    allievo = request.user.allievo
    with transaction.atomic():
        lezione = get_object_or_404(Lezione.objects.select_for_update(), pk=pk)

        if lezione.data < timezone.localdate() or lezione.stato == Lezione.Stato.ANNULLATA:
            messages.error(request, _("Questa lezione non è più prenotabile."))
            return redirect("lezioni:prenota")

        gia_attiva = (
            Partecipazione.objects.filter(lezione=lezione, allievo=allievo)
            .exclude(stato=Partecipazione.Stato.ANNULLATA)
            .exists()
        )
        if gia_attiva:
            messages.info(request, _("Sei già iscritto a questa lezione."))
            return redirect("persone:portale")

        capienza = lezione.tipo_lezione.capienza_max
        if capienza is not None:
            n_attivi = lezione.partecipazioni.exclude(stato=Partecipazione.Stato.ANNULLATA).count()
            if n_attivi >= capienza:
                messages.error(request, _("Questa lezione è nel frattempo diventata al completo."))
                return redirect("lezioni:prenota")

        Partecipazione.objects.update_or_create(
            lezione=lezione,
            allievo=allievo,
            defaults={"stato": Partecipazione.Stato.PREVISTA, "cavallo": None},
        )

    messages.success(request, _("Prenotazione registrata: il cavallo ti verrà assegnato dalla segreteria."))
    return redirect("persone:portale")


@allievo_required
@richiede_impostazione(_prenotazione_autonoma_attiva, "persone:portale", _MESSAGGIO_FEATURE_DISATTIVA)
def annulla_prenotazione(request, pk):
    if request.method != "POST":
        return redirect("persone:portale")

    partecipazione = get_object_or_404(Partecipazione, pk=pk, allievo=request.user.allievo)
    if partecipazione.lezione.data < timezone.localdate():
        messages.error(request, _("Non puoi annullare una lezione già passata."))
    else:
        partecipazione.stato = Partecipazione.Stato.ANNULLATA
        partecipazione.save(update_fields=["stato"])
        messages.success(request, _("Prenotazione annullata."))
    return redirect("persone:portale")
