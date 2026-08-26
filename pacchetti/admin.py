from django.contrib import admin

from core.admin_widgets import DATE_TIME_FORMFIELD_OVERRIDES

from .models import Pacchetto, TipoPacchetto


@admin.register(TipoPacchetto)
class TipoPacchettoAdmin(admin.ModelAdmin):
    list_display = ("nome", "numero_lezioni", "durata_giorni", "prezzo", "prezzo_scontato_pensione", "attivo")
    list_filter = ("attivo",)


@admin.register(Pacchetto)
class PacchettoAdmin(admin.ModelAdmin):
    list_display = ("allievo", "tipo_pacchetto", "data_inizio", "data_scadenza", "lezioni_residue", "stato")
    list_filter = ("stato", "tipo_pacchetto")
    search_fields = ("allievo__nome", "allievo__cognome")
    formfield_overrides = DATE_TIME_FORMFIELD_OVERRIDES
