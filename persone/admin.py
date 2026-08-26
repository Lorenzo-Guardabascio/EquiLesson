from django.contrib import admin

from .models import Allievo, Documento, Istruttore, Proprietario, Tutore


class DocumentoInline(admin.TabularInline):
    model = Documento
    extra = 0


@admin.register(Allievo)
class AllievoAdmin(admin.ModelAdmin):
    list_display = ("cognome", "nome", "stato", "certificato_medico_scadenza", "is_minorenne")
    list_filter = ("stato",)
    search_fields = ("nome", "cognome", "codice_fiscale")
    filter_horizontal = ("tutori",)
    inlines = [DocumentoInline]


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
