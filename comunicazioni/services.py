"""Invio email centralizzato per notifiche automatiche e broadcast."""

from django.conf import settings
from django.core.mail import EmailMessage, send_mail
from django.utils import timezone

from persone.models import Allievo


def invia_notifica_allievo(oggetto, corpo, allievo):
    """Invia un'email personale a un singolo allievo, se ha un indirizzo email."""
    if not allievo.email:
        return False
    send_mail(oggetto, corpo, settings.DEFAULT_FROM_EMAIL, [allievo.email])
    return True


def invia_broadcast(comunicazione, utente):
    """Invia una Comunicazione a tutti gli allievi attivi con email, in Bcc
    (i destinatari non devono vedersi gli indirizzi a vicenda) e aggiorna il record.
    """
    destinatari = list(
        Allievo.objects.filter(stato=Allievo.Stato.ATTIVO).exclude(email="").values_list("email", flat=True)
    )
    if destinatari:
        email = EmailMessage(
            subject=comunicazione.oggetto,
            body=comunicazione.corpo,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[settings.DEFAULT_FROM_EMAIL],
            bcc=destinatari,
        )
        email.send()

    comunicazione.inviata_da = utente
    comunicazione.inviata_il = timezone.now()
    comunicazione.destinatari_count = len(destinatari)
    comunicazione.save(update_fields=["inviata_da", "inviata_il", "destinatari_count"])
