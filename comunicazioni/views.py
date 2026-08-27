from django import forms
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import permission_required
from django.shortcuts import redirect, render
from django.utils.translation import gettext as _

from .models import Comunicazione
from .services import invia_broadcast


class ComunicazioneForm(forms.ModelForm):
    class Meta:
        model = Comunicazione
        fields = ["oggetto", "corpo"]
        widgets = {
            "oggetto": forms.TextInput(attrs={"class": "form-control"}),
            "corpo": forms.Textarea(attrs={"class": "form-control", "rows": 6}),
        }


@staff_member_required
@permission_required("comunicazioni.view_comunicazione", raise_exception=True)
def comunicazione_lista(request):
    comunicazioni = Comunicazione.objects.all()
    return render(request, "comunicazioni/lista.html", {
        "comunicazioni": comunicazioni,
        "puo_inviare": request.user.has_perm("comunicazioni.add_comunicazione"),
    })


@staff_member_required
@permission_required("comunicazioni.add_comunicazione", raise_exception=True)
def comunicazione_nuova(request):
    # Niente modifica/eliminazione da qui: una volta inviata una comunicazione
    # è uno storico (vedi Comunicazione.__doc__), la si compone e basta —
    # stesso comportamento di ComunicazioneAdmin.save_model.
    if request.method == "POST":
        form = ComunicazioneForm(request.POST)
        if form.is_valid():
            comunicazione = form.save()
            try:
                invia_broadcast(comunicazione, request.user)
            except Exception as exc:
                messages.error(
                    request,
                    _("Comunicazione salvata ma l'invio è fallito: %(errore)s") % {"errore": exc},
                )
            else:
                messages.success(
                    request,
                    _("Comunicazione inviata a %(n)s allievi.") % {"n": comunicazione.destinatari_count},
                )
            return redirect("comunicazioni:lista")
    else:
        form = ComunicazioneForm()
    return render(request, "comunicazioni/form.html", {"form": form})
