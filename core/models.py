from django.db import models


class Impostazioni(models.Model):
    """Impostazioni globali del gestionale — un solo record, sempre pk=1.

    Le credenziali/segreti (token bot Telegram, chiavi WhatsApp, SMTP) restano
    nel .env come le altre variabili d'ambiente: qui vivono solo interruttori
    e valori non sensibili che ha senso cambiare dall'admin senza toccare i file.
    """

    prenotazione_autonoma_abilitata = models.BooleanField(
        default=False,
        verbose_name="Prenotazione autonoma allievi abilitata",
        help_text=(
            "Se attivo, gli allievi possono prenotare/annullare da soli la propria "
            "partecipazione alle lezioni aperte dal portale. Se disattivo (default), "
            "le lezioni restano gestite solo da admin/segreteria."
        ),
    )
    email_notifiche_staff = models.EmailField(
        blank=True,
        verbose_name="Email notifiche staff",
        help_text=(
            "Destinatario degli alert automatici che non riguardano un allievo "
            "specifico (es. scadenze sanitarie dei cavalli). Se vuoto, quegli "
            "alert non vengono inviati."
        ),
    )
    notifiche_telegram_abilitate = models.BooleanField(
        default=False,
        verbose_name="Notifiche Telegram abilitate",
        help_text="Richiede TELEGRAM_BOT_TOKEN configurato nel .env (vedi README).",
    )
    notifiche_whatsapp_abilitate = models.BooleanField(
        default=False,
        verbose_name="Notifiche WhatsApp abilitate",
        help_text=(
            "Richiede un account WhatsApp Business Cloud API (Meta) configurato "
            "nel .env — questa piattaforma fornisce solo l'integrazione, non "
            "l'account (vedi README)."
        ),
    )

    class Meta:
        verbose_name = "impostazioni"
        verbose_name_plural = "impostazioni"

    def __str__(self):
        return "Impostazioni del gestionale"

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        pass  # singleton: non si cancella

    @classmethod
    def get(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj
