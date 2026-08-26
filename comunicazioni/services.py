"""Invio centralizzato: email (sempre), Telegram/WhatsApp (se collegati/abilitati)."""

import logging

from django.conf import settings
from django.core.mail import EmailMessage, send_mail
from django.utils import timezone

from core.models import Impostazioni
from persone.models import Allievo

from .canali import telegram, whatsapp

logger = logging.getLogger(__name__)


def invia_notifica_allievo(oggetto, corpo, allievo):
    """Invia un promemoria/alert personale su ogni canale disponibile e
    abilitato per quell'allievo (email, Telegram, WhatsApp). I canali sono
    additivi, non alternativi: se un allievo ha collegato Telegram riceve
    comunque anche l'email, se ne ha una. Ritorna True se è stato inviato
    su almeno un canale.
    """
    inviato = False

    if allievo.email:
        send_mail(oggetto, corpo, settings.DEFAULT_FROM_EMAIL, [allievo.email])
        inviato = True

    impostazioni = Impostazioni.get()
    testo_messaggio = f"{oggetto}\n\n{corpo}"

    if impostazioni.notifiche_telegram_abilitate:
        link = getattr(allievo, "telegram_link", None)
        if link and link.collegato:
            try:
                telegram.invia_messaggio(link.chat_id, testo_messaggio)
                inviato = True
            except Exception:
                logger.exception("Invio Telegram fallito per l'allievo %s", allievo.pk)

    if impostazioni.notifiche_whatsapp_abilitate and allievo.telefono:
        try:
            whatsapp.invia_messaggio(allievo.telefono, testo_messaggio)
            inviato = True
        except Exception:
            logger.exception("Invio WhatsApp fallito per l'allievo %s", allievo.pk)

    return inviato


def invia_notifica_staff(oggetto, corpo):
    """Invia un alert via email all'indirizzo staff configurato in Impostazioni
    (per avvisi che non riguardano un allievo specifico, es. scadenze sanitarie
    dei cavalli). Ritorna True se inviato, False se nessun indirizzo è configurato.
    """
    email_staff = Impostazioni.get().email_notifiche_staff
    if not email_staff:
        return False
    send_mail(oggetto, corpo, settings.DEFAULT_FROM_EMAIL, [email_staff])
    return True


def invia_broadcast(comunicazione, utente):
    """Invia una Comunicazione a tutti gli allievi attivi con email, in Bcc
    (i destinatari non devono vedersi gli indirizzi a vicenda), più Telegram
    per chi l'ha collegato, e aggiorna il record.
    """
    allievi_attivi = Allievo.objects.filter(stato=Allievo.Stato.ATTIVO)
    destinatari_email = list(allievi_attivi.exclude(email="").values_list("email", flat=True))

    if destinatari_email:
        email = EmailMessage(
            subject=comunicazione.oggetto,
            body=comunicazione.corpo,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[settings.DEFAULT_FROM_EMAIL],
            bcc=destinatari_email,
        )
        email.send()

    n_telegram = 0
    if Impostazioni.get().notifiche_telegram_abilitate:
        testo_messaggio = f"{comunicazione.oggetto}\n\n{comunicazione.corpo}"
        for allievo in allievi_attivi.select_related("telegram_link"):
            link = getattr(allievo, "telegram_link", None)
            if link and link.collegato:
                try:
                    telegram.invia_messaggio(link.chat_id, testo_messaggio)
                    n_telegram += 1
                except Exception:
                    logger.exception("Broadcast Telegram fallito per l'allievo %s", allievo.pk)

    comunicazione.inviata_da = utente
    comunicazione.inviata_il = timezone.now()
    # Conteggio "destinatari" = indirizzi email raggiunti; il Bcc non permette
    # di sapere quanti sono stati effettivamente consegnati, ma è la stessa
    # metrica informativa usata finora. I destinatari Telegram si vedono nel
    # log applicativo, non qui, per non complicare un campo che è solo a scopo
    # di controllo in admin.
    comunicazione.destinatari_count = len(destinatari_email)
    comunicazione.save(update_fields=["inviata_da", "inviata_il", "destinatari_count"])
