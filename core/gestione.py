"""Viste generiche per le voci di "Gestione" registrate in gestione_config.

Una sola implementazione di lista/form/elimina per tutte le voci, invece di
9 viste quasi identiche: ognuna si comporta secondo i dati dichiarati nella
sua Voce (core/gestione_config.py). Stesso stile del resto del progetto —
funzioni + decoratori, non class-based views — solo parametrizzato sulla
voce invece che sul singolo modello.
"""
from django import forms
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.core.exceptions import PermissionDenied
from django.db import models as db_models
from django.db import transaction
from django.db.models import Q
from django.forms import inlineformset_factory, modelform_factory
from django.shortcuts import get_object_or_404, redirect, render
from django.template import Variable, VariableDoesNotExist
from django.urls import reverse
from django.utils.translation import gettext as _

from .gestione_config import REGISTRO


def _voce_o_404(slug):
    voce = REGISTRO.get(slug)
    if voce is None:
        from django.http import Http404
        raise Http404(f"Voce di gestione sconosciuta: {slug}")
    return voce


def _richiede_permesso(request, voce, azione):
    if not request.user.has_perm(voce.permesso(azione)):
        raise PermissionDenied


def _valore(oggetto, percorso):
    """Risolve 'get_stato_display' o 'allievo.nome' come farebbe {{ obj.x }}
    nei template — stessa semantica (attributo, chiave, indice, chiamata),
    riusata qui per non duplicarla a mano voce per voce."""
    try:
        valore = Variable(f"o.{percorso}").resolve({"o": oggetto})
    except (VariableDoesNotExist, Exception):
        return ""
    if isinstance(valore, bool):
        # Altrimenti in tabella compare il letterale Python "True"/"False"
        # invece di un testo leggibile — capitato con i campi booleani
        # (attivo, disponibile...) usati come colonna.
        return _("Sì") if valore else _("No")
    return valore


def _formfield_callback(f, **kwargs):
    """Applica a QUALSIASI campo generato le stesse regole già in vigore nel
    resto del sito: input nativi per data/ora (niente testo libero
    travestito da widget, vedi core/admin_widgets.py) e classi Bootstrap +
    data-searchable per i menu a tendina (vedi lezioni/forms.py) — qui in un
    solo posto invece che dichiarato a mano per ogni singolo campo di ogni
    singolo modello, così nessun campo nuovo può restare fuori per
    dimenticanza."""
    if isinstance(f, db_models.DateField) and not isinstance(f, db_models.DateTimeField):
        kwargs.setdefault("widget", forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"))
        kwargs.setdefault("input_formats", ["%Y-%m-%d"])
    elif isinstance(f, db_models.TimeField):
        kwargs.setdefault("widget", forms.TimeInput(attrs={"type": "time"}, format="%H:%M"))
        kwargs.setdefault("input_formats", ["%H:%M", "%H:%M:%S"])

    formfield = f.formfield(**kwargs)
    if formfield is None:
        return formfield

    widget = formfield.widget
    if isinstance(widget, forms.CheckboxInput):
        widget.attrs.setdefault("class", "form-check-input")
    elif isinstance(widget, forms.CheckboxSelectMultiple):
        pass
    elif isinstance(widget, (forms.Select, forms.SelectMultiple)):
        widget.attrs.setdefault("class", "form-select")
        widget.attrs.setdefault("data-searchable", "true")
    else:
        widget.attrs.setdefault("class", "form-control")
    return formfield


def _form_class(voce):
    return modelform_factory(voce.model, fields=voce.campi_form, formfield_callback=_formfield_callback)


def _formset_class(voce):
    if not voce.inline:
        return None
    return inlineformset_factory(
        voce.model, voce.inline.model,
        fields=voce.inline.campi, fk_name=voce.inline.fk_name,
        extra=voce.inline.extra, can_delete=True,
        formfield_callback=_formfield_callback,
    )


@staff_member_required
def gestione_lista(request, slug):
    voce = _voce_o_404(slug)
    _richiede_permesso(request, voce, "view")

    qs = voce.model.objects.all()
    q = request.GET.get("q", "").strip()
    if q and voce.cerca_campi:
        condizione = Q()
        for campo in voce.cerca_campi:
            condizione |= Q(**{f"{campo}__icontains": q})
        qs = qs.filter(condizione)

    righe = [
        {"pk": oggetto.pk, "valori": [_valore(oggetto, percorso) for _, percorso in voce.colonne]}
        for oggetto in qs
    ]

    return render(request, "core/gestione_lista.html", {
        "voce": voce,
        "righe": righe,
        "q": q,
        "puo_scrivere": request.user.has_perm(voce.permesso("change")),
        "puo_aggiungere": request.user.has_perm(voce.permesso("add")),
        "puo_eliminare": request.user.has_perm(voce.permesso("delete")),
    })


@staff_member_required
def gestione_form(request, slug, pk=None):
    voce = _voce_o_404(slug)
    if voce.sola_lettura:
        raise PermissionDenied
    _richiede_permesso(request, voce, "change" if pk else "add")

    istanza = get_object_or_404(voce.model, pk=pk) if pk else None
    FormClass = _form_class(voce)
    FormSetClass = _formset_class(voce)

    if request.method == "POST":
        form = FormClass(request.POST, request.FILES, instance=istanza)
        with transaction.atomic():
            if form.is_valid():
                oggetto = form.save()
                formset = FormSetClass(request.POST, request.FILES, instance=oggetto) if FormSetClass else None
                if formset is None or formset.is_valid():
                    if formset:
                        formset.save()
                    messages.success(request, _("%(voce)s salvato correttamente.") % {"voce": voce.etichetta_singolare.capitalize()})
                    return redirect("core:gestione_lista", slug=slug)
                transaction.set_rollback(True)
            else:
                formset = FormSetClass(request.POST, request.FILES, instance=istanza or voce.model()) if FormSetClass else None
    else:
        form = FormClass(instance=istanza)
        formset = FormSetClass(instance=istanza) if FormSetClass else None

    return render(request, "core/gestione_form.html", {
        "voce": voce,
        "form": form,
        "formset": formset,
        "istanza": istanza,
    })


@staff_member_required
def gestione_elimina(request, slug, pk):
    voce = _voce_o_404(slug)
    if voce.sola_lettura:
        raise PermissionDenied
    _richiede_permesso(request, voce, "delete")

    oggetto = get_object_or_404(voce.model, pk=pk)
    if request.method == "POST":
        oggetto.delete()
        messages.success(request, _("%(voce)s eliminato.") % {"voce": voce.etichetta_singolare.capitalize()})
        return redirect("core:gestione_lista", slug=slug)

    return render(request, "core/gestione_conferma_elimina.html", {
        "voce": voce,
        "oggetto": oggetto,
    })
