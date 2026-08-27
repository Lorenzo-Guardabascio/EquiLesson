from datetime import timedelta

from django import forms
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import permission_required
from django.shortcuts import redirect, render
from django.utils import timezone
from django.utils.translation import gettext as _

from cavalli.models import Cavallo
from lezioni.models import Lezione
from persone.models import Allievo

from .models import Impostazioni


def home(request):
    context = {}
    if request.user.is_authenticated and request.user.is_staff:
        oggi = timezone.localdate()
        context.update(
            n_allievi_attivi=Allievo.objects.filter(stato=Allievo.Stato.ATTIVO).count(),
            n_cavalli=Cavallo.objects.count(),
            n_lezioni_oggi=Lezione.objects.filter(data=oggi).count(),
            prossime_lezioni=Lezione.objects.filter(data__gte=oggi)
            .select_related("tipo_lezione")
            .order_by("data", "ora_inizio")[:5],
            scadenze_certificati=Allievo.objects.filter(
                certificato_medico_scadenza__isnull=False,
                certificato_medico_scadenza__lte=oggi + timedelta(days=30),
            ).order_by("certificato_medico_scadenza")[:5],
        )
    return render(request, "core/home.html", context)


class ImpostazioniForm(forms.ModelForm):
    class Meta:
        model = Impostazioni
        fields = [
            "prenotazione_autonoma_abilitata",
            "email_notifiche_staff",
            "notifiche_telegram_abilitate",
            "notifiche_whatsapp_abilitate",
        ]
        widgets = {
            "prenotazione_autonoma_abilitata": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "email_notifiche_staff": forms.EmailInput(attrs={"class": "form-control"}),
            "notifiche_telegram_abilitate": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "notifiche_whatsapp_abilitate": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }


@staff_member_required
@permission_required("core.change_impostazioni", raise_exception=True)
def impostazioni_form(request):
    istanza = Impostazioni.get()
    if request.method == "POST":
        form = ImpostazioniForm(request.POST, instance=istanza)
        if form.is_valid():
            form.save()
            messages.success(request, _("Impostazioni salvate."))
            return redirect("core:impostazioni")
    else:
        form = ImpostazioniForm(instance=istanza)
    return render(request, "core/impostazioni_form.html", {"form": form})
