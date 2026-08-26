"""Widget data/ora condivisi per l'admin di Django.

Di default l'admin di Django rende DateField/TimeField come `<input
type="text">` con una piccola icona calendario iniettata via JavaScript
(DateTimeShortcuts.js): l'icona funziona, ma NON impedisce affatto di
digitare testo libero nel campo — la validazione arriva solo al submit.
Verificato in pratica: si può scrivere una frase qualsiasi al posto di una
data e il campo la accetta senza alcun avviso finché non si salva.

Qui si sostituisce quel widget con gli input nativi del browser
(type="date"/type="time"), la stessa soluzione già usata nel form lezione
custom: il browser stesso impedisce l'inserimento di un valore non valido,
non serve fidarsi di JavaScript aggiuntivo che potrebbe anche non caricarsi.

Uso: `formfield_overrides = DATE_TIME_FORMFIELD_OVERRIDES` in un ModelAdmin.
"""

from django import forms
from django.db import models

DATE_TIME_FORMFIELD_OVERRIDES = {
    models.DateField: {
        "widget": forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"),
        "input_formats": ["%Y-%m-%d"],
    },
    models.TimeField: {
        "widget": forms.TimeInput(attrs={"type": "time"}, format="%H:%M"),
        "input_formats": ["%H:%M", "%H:%M:%S"],
    },
}
