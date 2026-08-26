from django import forms
from django.forms import inlineformset_factory

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
            "tipo_lezione": forms.Select(attrs=SELECT_ATTRS),
            "istruttore": forms.Select(attrs=SELECT_ATTRS),
            "campo": forms.Select(attrs=SELECT_ATTRS),
            "stato": forms.Select(attrs=SELECT_ATTRS),
            "note": forms.Textarea(attrs={**INPUT_ATTRS, "rows": 2}),
        }


PartecipazioneFormSet = inlineformset_factory(
    Lezione,
    Partecipazione,
    fields=["allievo", "cavallo", "pacchetto", "stato", "note"],
    extra=1,
    can_delete=True,
    widgets={
        "allievo": forms.Select(attrs=SELECT_ATTRS),
        "cavallo": forms.Select(attrs=SELECT_ATTRS),
        "pacchetto": forms.Select(attrs=SELECT_ATTRS),
        "stato": forms.Select(attrs=SELECT_ATTRS),
        "note": forms.TextInput(attrs=INPUT_ATTRS),
    },
)
