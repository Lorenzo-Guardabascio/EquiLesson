from django.contrib import admin, messages

from .models import Comunicazione, NotificaInviata, TelegramLink
from .services import invia_broadcast


@admin.register(NotificaInviata)
class NotificaInviataAdmin(admin.ModelAdmin):
    """Sola lettura: è il log di cosa è già stato inviato da `invia_notifiche`.

    È possibile eliminare una riga per forzare un nuovo invio dello stesso avviso.
    """

    list_display = ("tipo", "allievo", "riferimento", "creata_il")
    list_filter = ("tipo",)
    search_fields = ("allievo__nome", "allievo__cognome")
    date_hierarchy = "creata_il"

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(Comunicazione)
class ComunicazioneAdmin(admin.ModelAdmin):
    """Compone e invia un broadcast a tutti gli allievi attivi.

    Salvare una nuova comunicazione la invia subito via email; una volta
    inviata resta come storico e non è più modificabile.
    """

    list_display = ("oggetto", "creata_il", "inviata_il", "destinatari_count", "inviata_da")
    readonly_fields = ("inviata_da", "inviata_il", "destinatari_count", "creata_il")

    def get_fields(self, request, obj=None):
        if obj:
            return ["oggetto", "corpo", "inviata_da", "inviata_il", "destinatari_count", "creata_il"]
        return ["oggetto", "corpo"]

    def has_change_permission(self, request, obj=None):
        # Una volta inviata è uno storico: non si modifica più.
        if obj and obj.inviata_il:
            return False
        return super().has_change_permission(request, obj)

    def save_model(self, request, obj, form, change):
        is_new = obj.pk is None
        super().save_model(request, obj, form, change)
        if not is_new:
            return
        try:
            invia_broadcast(obj, request.user)
        except Exception as exc:
            self.message_user(
                request,
                f"Comunicazione salvata ma l'invio email è fallito: {exc}",
                level=messages.ERROR,
            )
        else:
            self.message_user(
                request, f"Comunicazione inviata a {obj.destinatari_count} allievi.", level=messages.SUCCESS
            )


@admin.register(TelegramLink)
class TelegramLinkAdmin(admin.ModelAdmin):
    """Sola consultazione: il collegamento lo fa l'allievo dal portale via `telegram_poll`."""

    list_display = ("allievo", "collegato", "collegato_il")
    list_filter = ("collegato_il",)
    search_fields = ("allievo__nome", "allievo__cognome")
    readonly_fields = ("allievo", "chat_id", "codice_collegamento", "collegato_il")

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
