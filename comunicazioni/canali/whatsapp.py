"""Invio messaggi WhatsApp via Meta WhatsApp Business Cloud API.

ATTENZIONE — a differenza del canale Telegram, questo modulo non è mai stato
testato contro l'API reale: richiede un account WhatsApp Business verificato
da Meta (numero di telefono dedicato, app su Meta for Developers, token
d'accesso), che questa piattaforma non fornisce e non può fornire da sola.
Attivarlo significa configurare quell'account per conto proprio (vedi
README) — il codice qui sotto segue la forma documentata dell'API ma va
verificato con credenziali reali prima di fare affidamento sull'invio.

Altra differenza importante: fuori dalla finestra di 24 ore da un messaggio
dell'utente, Meta richiede un "message template" pre-approvato invece di
testo libero — questa funzione invia solo testo libero, quindi funziona solo
entro quella finestra o per i primi test.
"""

import json
import urllib.error
import urllib.request

from django.conf import settings

TIMEOUT_SECONDI = 10


class WhatsAppNonConfigurato(Exception):
    """WHATSAPP_ACCESS_TOKEN o WHATSAPP_PHONE_NUMBER_ID non impostati nel .env."""


def invia_messaggio(numero_destinatario, testo):
    """Invia un messaggio di testo libero. Solleva RuntimeError se fallisce."""
    if not settings.WHATSAPP_ACCESS_TOKEN or not settings.WHATSAPP_PHONE_NUMBER_ID:
        raise WhatsAppNonConfigurato(
            "WHATSAPP_ACCESS_TOKEN/WHATSAPP_PHONE_NUMBER_ID non configurati nel .env."
        )

    url = f"https://graph.facebook.com/v19.0/{settings.WHATSAPP_PHONE_NUMBER_ID}/messages"
    corpo = {
        "messaging_product": "whatsapp",
        "to": numero_destinatario,
        "type": "text",
        "text": {"body": testo},
    }
    richiesta = urllib.request.Request(
        url,
        data=json.dumps(corpo).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {settings.WHATSAPP_ACCESS_TOKEN}",
        },
    )
    try:
        with urllib.request.urlopen(richiesta, timeout=TIMEOUT_SECONDI) as risposta:
            risposta.read()
    except urllib.error.HTTPError as exc:
        dettaglio = json.loads(exc.read().decode("utf-8"))
        raise RuntimeError(f"WhatsApp ha rifiutato la richiesta: {dettaglio}")
