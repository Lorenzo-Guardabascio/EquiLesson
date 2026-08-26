from django.contrib import admin

from core.admin_widgets import DATE_TIME_FORMFIELD_OVERRIDES

from .models import Campo, Lezione, Partecipazione, TipoLezione


class PartecipazioneInline(admin.TabularInline):
    model = Partecipazione
    extra = 1


@admin.register(Lezione)
class LezioneAdmin(admin.ModelAdmin):
    list_display = ("data", "ora_inizio", "ora_fine", "tipo_lezione", "istruttore", "campo", "stato")
    list_filter = ("stato", "tipo_lezione", "campo", "istruttore")
    date_hierarchy = "data"
    inlines = [PartecipazioneInline]
    formfield_overrides = DATE_TIME_FORMFIELD_OVERRIDES


@admin.register(Campo)
class CampoAdmin(admin.ModelAdmin):
    list_display = ("nome", "note")


@admin.register(TipoLezione)
class TipoLezioneAdmin(admin.ModelAdmin):
    list_display = ("nome", "durata_default_minuti", "capienza_max", "attivo")
    list_filter = ("attivo",)


@admin.register(Partecipazione)
class PartecipazioneAdmin(admin.ModelAdmin):
    list_display = ("lezione", "allievo", "cavallo", "stato", "pacchetto")
    list_filter = ("stato",)
    search_fields = ("allievo__nome", "allievo__cognome")
