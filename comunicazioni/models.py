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

    tipo = models.CharField(max_length=30, choices=Tipo.choices)
    allievo = models.ForeignKey(Allievo, on_delete=models.CASCADE, related_name="notifiche_inviate")
    riferimento = models.DateField(help_text="Data a cui si riferisce l'avviso (lezione o scadenza).")
    creata_il = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("tipo", "allievo", "riferimento")
        ordering = ["-creata_il"]
        verbose_name = "notifica inviata"
        verbose_name_plural = "notifiche inviate"

    def __str__(self):
        return f"{self.get_tipo_display()} - {self.allievo} ({self.riferimento:%d/%m/%Y})"


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
