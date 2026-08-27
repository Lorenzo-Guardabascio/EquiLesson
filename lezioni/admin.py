from django.contrib import admin

from core.admin_widgets import DATE_TIME_FORMFIELD_OVERRIDES

from .models import Campo, Lezione, Partecipazione, TipoLezione


class SolaConsultazioneMixin:
    """Niente creare/modificare/eliminare da qui: un solo posto dove si
    gestiscono davvero le lezioni (il form custom in /lezioni/), non due
    interfacce parallele sugli stessi dati che finiscono per disallinearsi
    (validazioni ed automatismi del form custom non esisterebbero passando
    da qui). L'admin resta utile solo per guardare/cercare.
    """

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class PartecipazioneInline(SolaConsultazioneMixin, admin.TabularInline):
    model = Partecipazione
    extra = 0


@admin.register(Lezione)
class LezioneAdmin(SolaConsultazioneMixin, admin.ModelAdmin):
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
class PartecipazioneAdmin(SolaConsultazioneMixin, admin.ModelAdmin):
    list_display = ("lezione", "allievo", "cavallo", "stato")
    list_filter = ("stato",)
    search_fields = ("allievo__nome", "allievo__cognome")
