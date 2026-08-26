from datetime import datetime

from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from .forms import LezioneForm, PartecipazioneFormSet
from .models import Lezione

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
                    messages.success(request, "Lezione salvata correttamente.")
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
        messages.success(request, "Lezione eliminata.")
        return redirect("lezioni:calendario")
    return render(request, "lezioni/lezione_conferma_elimina.html", {"lezione": lezione})
