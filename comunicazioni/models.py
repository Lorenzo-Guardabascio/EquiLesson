from django.conf import settings
from django.db import models

from persone.models import Allievo


class NotificaInviata(models.Model):
    """Registro delle notifiche automatiche già inviate.

    Serve solo a evitare invii duplicati quando il comando `invia_notifiche`
    gira più volte (es. da cron ogni giorno): per una data combinazione di
    tipo/allievo/riferimento si invia una volta sola. Se la scadenza cambia
    (es. certificato rinnovato) il riferimento cambia e l'avviso può ripartire.
    """

    class Tipo(models.TextChoices):
        PROMEMORIA_LEZIONE = "promemoria_lezione", "Promemoria lezione"
        SCADENZA_CERTIFICATO = "scadenza_certificato", "Scadenza certificato medico"
        SCADENZA_FISE = "scadenza_fise", "Scadenza tessera FISE"
        SCADENZA_FITETREK = "scadenza_fitetrek", "Scadenza tessera FITETREK"
        SCADENZA_PACCHETTO = "scadenza_pacchetto", "Scadenza pacchetto"
        SCADENZA_SANITARIA_CAVALLO = "scadenza_sanitaria_cavallo", "Scadenza sanitaria cavallo"

    tipo = models.CharField(max_length=30, choices=Tipo.choices)
    # Uno solo dei due è valorizzato: allievo per le notifiche personali,
    # cavallo per le scadenze sanitarie (che vanno allo staff, non a un
    # allievo). Entrambi nullable per questo — i controlli di deduplica
    # includono sempre esplicitamente entrambi i campi, non solo uno, così
    # due cavalli diversi con la stessa scadenza non si scavalcano a vicenda.
    allievo = models.ForeignKey(
        Allievo, on_delete=models.CASCADE, null=True, blank=True, related_name="notifiche_inviate"
    )
    cavallo = models.ForeignKey(
        "cavalli.Cavallo", on_delete=models.CASCADE, null=True, blank=True, related_name="notifiche_inviate"
    )
    riferimento = models.DateField(help_text="Data a cui si riferisce l'avviso (lezione o scadenza).")
    creata_il = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("tipo", "allievo", "cavallo", "riferimento")
        ordering = ["-creata_il"]
        verbose_name = "notifica inviata"
        verbose_name_plural = "notifiche inviate"

    def __str__(self):
        soggetto = self.allievo or self.cavallo
        return f"{self.get_tipo_display()} - {soggetto} ({self.riferimento:%d/%m/%Y})"


class Comunicazione(models.Model):
    """Messaggio broadcast inviato via email a tutti gli allievi attivi
    (es. 'campo chiuso per pioggia'). Funziona anche da storico: una volta
    inviata non è più modificabile.
    """

    oggetto = models.CharField(max_length=200)
    corpo = models.TextField()
    inviata_da = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="comunicazioni_inviate",
    )
    inviata_il = models.DateTimeField(null=True, blank=True)
    destinatari_count = models.PositiveIntegerField(default=0)
    creata_il = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-creata_il"]
        verbose_name = "comunicazione"
        verbose_name_plural = "comunicazioni"

    def __str__(self):
        return self.oggetto


class TelegramLink(models.Model):
    """Collegamento tra un Allievo e la sua chat Telegram (per l'invio notifiche).

    Il collegamento avviene per polling (`manage.py telegram_poll`), non via
    webhook: il server non è esposto su internet, quindi non può ricevere
    richieste in ingresso da Telegram — deve essere lui a chiedere gli
    aggiornamenti a intervalli regolari.
    """

    allievo = models.OneToOneField(Allievo, on_delete=models.CASCADE, related_name="telegram_link")
    chat_id = models.CharField(max_length=64, blank=True)
    codice_collegamento = models.CharField(
        max_length=12,
        blank=True,
        help_text="Codice mostrato all'allievo nel portale, da inviare al bot per collegare l'account.",
    )
    collegato_il = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "collegamento Telegram"
        verbose_name_plural = "collegamenti Telegram"

    def __str__(self):
        stato = "collegato" if self.chat_id else "non collegato"
        return f"{self.allievo} ({stato})"

    @property
    def collegato(self):
        return bool(self.chat_id)


class TelegramPollState(models.Model):
    """Tiene il segnalibro (update_id) dell'ultimo messaggio Telegram già letto.

    Singleton (pk=1): un solo bot, un solo cursore di lettura condiviso da
    ogni esecuzione di `manage.py telegram_poll`.
    """

    ultimo_update_id = models.BigIntegerField(default=0)

    class Meta:
        verbose_name = "stato polling Telegram"
        verbose_name_plural = "stato polling Telegram"

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def get(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj
