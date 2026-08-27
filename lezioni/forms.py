from django import forms
from django.forms import inlineformset_factory

from pacchetti.models import Pacchetto

from .models import Lezione, Partecipazione

SELECT_ATTRS = {"class": "form-select"}
INPUT_ATTRS = {"class": "form-control"}


class LezioneForm(forms.ModelForm):
    # Campi ridichiarati esplicitamente per usare gli input nativi del browser
    # (type="date"/"time") invece del vecchio calendario JS dell'admin di Django.
    # input_formats deve corrispondere al formato che il browser invia (ISO),
    # indipendentemente dalla localizzazione italiana usata altrove nel sito.
    data = forms.DateField(
        widget=forms.DateInput(attrs={**INPUT_ATTRS, "type": "date"}, format="%Y-%m-%d"),
        input_formats=["%Y-%m-%d"],
    )
    ora_inizio = forms.TimeField(
        widget=forms.TimeInput(attrs={**INPUT_ATTRS, "type": "time"}, format="%H:%M"),
        input_formats=["%H:%M", "%H:%M:%S"],
    )
    ora_fine = forms.TimeField(
        widget=forms.TimeInput(attrs={**INPUT_ATTRS, "type": "time"}, format="%H:%M"),
        input_formats=["%H:%M", "%H:%M:%S"],
    )

    class Meta:
        model = Lezione
        fields = ["data", "ora_inizio", "ora_fine", "tipo_lezione", "istruttore", "campo", "stato", "note"]
        widgets = {
            "tipo_lezione": forms.Select(attrs={**SELECT_ATTRS, "data-searchable": "true"}),
            "istruttore": forms.Select(attrs={**SELECT_ATTRS, "data-searchable": "true"}),
            "campo": forms.Select(attrs={**SELECT_ATTRS, "data-searchable": "true"}),
            "stato": forms.Select(attrs=SELECT_ATTRS),
            "note": forms.Textarea(attrs={**INPUT_ATTRS, "rows": 2}),
        }


class PacchettoSelect(forms.Select):
    """Select per il pacchetto che espone l'allievo proprietario di ogni opzione.

    Serve alla riga JS lato client per mostrare solo i pacchetti dell'allievo
    scelto in quella stessa riga di partecipazione — la validazione vera
    resta comunque server-side in PartecipazioneForm.clean(), questo è solo
    per l'usabilità (evitare di dover cercare a occhio in un elenco di
    pacchetti di TUTTI gli allievi).

    La mappa pacchetto->allievo si interroga in `optgroups()`, non in
    `__init__`: il widget è un'istanza condivisa a livello di classe (vive
    per tutta la vita del processo), quindi interrogare il DB nel costruttore
    la congelerebbe alla prima richiesta (pacchetti creati dopo non
    comparirebbero più) — oltre a rompere `manage.py migrate` su un database
    ancora vuoto, dato che il modulo si importa prima che le tabelle esistano.
    """

    def optgroups(self, name, value, attrs=None):
        self._allievo_per_pacchetto = dict(Pacchetto.objects.values_list("pk", "allievo_id"))
        return super().optgroups(name, value, attrs)

    def create_option(self, name, value, label, selected, index, subindex=None, attrs=None):
        option = super().create_option(name, value, label, selected, index, subindex, attrs)
        pk = value.value if hasattr(value, "value") else value
        allievo_id = getattr(self, "_allievo_per_pacchetto", {}).get(pk)
        if allievo_id is not None:
            option["attrs"]["data-allievo"] = allievo_id
        return option


class PartecipazioneForm(forms.ModelForm):
    class Meta:
        model = Partecipazione
        fields = ["allievo", "cavallo", "pacchetto", "stato", "note"]
        widgets = {
            "allievo": forms.Select(attrs={**SELECT_ATTRS, "data-searchable": "true", "data-role": "allievo"}),
            "cavallo": forms.Select(attrs={**SELECT_ATTRS, "data-searchable": "true"}),
            "pacchetto": PacchettoSelect(attrs={**SELECT_ATTRS, "data-role": "pacchetto"}),
            "stato": forms.Select(attrs=SELECT_ATTRS),
            "note": forms.TextInput(attrs=INPUT_ATTRS),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Pacchetto.__str__ attraversa sia allievo che tipo_pacchetto: senza
        # select_related, stampare tutte le opzioni di questo <select> (una
        # per pacchetto esistente) costerebbe 2 query in più per ciascuna.
        self.fields["pacchetto"].queryset = Pacchetto.objects.select_related("allievo", "tipo_pacchetto")

    def clean(self):
        cleaned = super().clean()
        allievo = cleaned.get("allievo")
        pacchetto = cleaned.get("pacchetto")
        if allievo and pacchetto and pacchetto.allievo_id != allievo.pk:
            self.add_error(
                "pacchetto",
                f"Questo pacchetto appartiene a {pacchetto.allievo}, non a {allievo}: "
                "sceglierne uno dell'allievo selezionato.",
            )
        return cleaned


PartecipazioneFormSet = inlineformset_factory(
    Lezione,
    Partecipazione,
    form=PartecipazioneForm,
    extra=1,
    can_delete=True,
)
