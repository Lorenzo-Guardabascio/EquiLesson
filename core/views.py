from datetime import timedelta

from django.shortcuts import render
from django.utils import timezone

from cavalli.models import Cavallo
from lezioni.models import Lezione
from persone.models import Allievo


def home(request):
    context = {}
    if request.user.is_authenticated and request.user.is_staff:
        oggi = timezone.localdate()
        context.update(
            n_allievi_attivi=Allievo.objects.filter(stato=Allievo.Stato.ATTIVO).count(),
            n_cavalli=Cavallo.objects.count(),
            n_lezioni_oggi=Lezione.objects.filter(data=oggi).count(),
            prossime_lezioni=Lezione.objects.filter(data__gte=oggi).order_by("data", "ora_inizio")[:5],
            scadenze_certificati=Allievo.objects.filter(
                certificato_medico_scadenza__isnull=False,
                certificato_medico_scadenza__lte=oggi + timedelta(days=30),
            ).order_by("certificato_medico_scadenza")[:5],
        )
    return render(request, "core/home.html", context)
