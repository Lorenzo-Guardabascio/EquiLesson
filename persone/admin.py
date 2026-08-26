from django.contrib import admin

from core.admin_widgets import DATE_TIME_FORMFIELD_OVERRIDES

from .models import Allievo, ConsensoLog, Documento, Istruttore, Proprietario, Tutore


class DocumentoInline(admin.TabularInline):
    model = Documento
    extra = 0


class ConsensoLogInline(admin.TabularInline):
    """Sola lettura: il consenso lo accetta l'allievo dal portale, non lo si inventa qui."""

    model = ConsensoLog
    extra = 0
    fields = ("tipo", "accettato_il", "indirizzo_ip", "testo_accettato")
    readonly_fields = fields

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(Allievo)
class AllievoAdmin(admin.ModelAdmin):
    list_display = ("cognome", "nome", "stato", "certificato_medico_scadenza", "is_minorenne")
    list_filter = ("stato",)
    search_fields = ("nome", "cognome", "codice_fiscale")
    filter_horizontal = ("tutori",)
    inlines = [DocumentoInline, ConsensoLogInline]
    formfield_overrides = DATE_TIME_FORMFIELD_OVERRIDES


@admin.register(Tutore)
class TutoreAdmin(admin.ModelAdmin):
    list_display = ("cognome", "nome", "relazione", "telefono")
    search_fields = ("nome", "cognome")


@admin.register(Istruttore)
class IstruttoreAdmin(admin.ModelAdmin):
    list_display = ("cognome", "nome", "attivo", "telefono")
    list_filter = ("attivo",)
    search_fields = ("nome", "cognome")


@admin.register(Proprietario)
class ProprietarioAdmin(admin.ModelAdmin):
    list_display = ("cognome", "nome", "telefono")
    search_fields = ("nome", "cognome")


@admin.register(Documento)
class DocumentoAdmin(admin.ModelAdmin):
    list_display = ("allievo", "tipo", "caricato_il")
    list_filter = ("tipo",)
