from django.contrib import admin

from core.admin_widgets import DATE_TIME_FORMFIELD_OVERRIDES

from .models import Cavallo, ScadenzaSanitaria


class ScadenzaSanitariaInline(admin.TabularInline):
    model = ScadenzaSanitaria
    extra = 0
    formfield_overrides = DATE_TIME_FORMFIELD_OVERRIDES


@admin.register(Cavallo)
class CavalloAdmin(admin.ModelAdmin):
    list_display = ("nome", "tipo", "livello_impiego", "disponibile", "proprietario")
    list_filter = ("tipo", "livello_impiego", "disponibile")
    search_fields = ("nome", "microchip")
    formfield_overrides = DATE_TIME_FORMFIELD_OVERRIDES
    inlines = [ScadenzaSanitariaInline]


@admin.register(ScadenzaSanitaria)
class ScadenzaSanitariaAdmin(admin.ModelAdmin):
    list_display = ("cavallo", "tipo", "data_scadenza", "note")
    list_filter = ("tipo",)
    search_fields = ("cavallo__nome",)
    formfield_overrides = DATE_TIME_FORMFIELD_OVERRIDES
