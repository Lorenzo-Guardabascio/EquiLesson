"""Invio e ricezione messaggi Telegram via Bot API, senza dipendenze esterne
(solo `urllib`/`json` di libreria standard — niente pacchetto `requests`).

Il collegamento avviene per polling (`manage.py telegram_poll`), non via
webhook: un server senza IP pubblico non può ricevere richieste in ingresso
da Telegram, ma può interrogarlo lui a intervalli regolari con `getUpdates`.
"""

import json
import urllib.error
import urllib.request

from django.conf import settings

TIMEOUT_SECONDI = 10


class TelegramNonConfigurato(Exception):
    """TELEGRAM_BOT_TOKEN non impostato nel .env."""


def _url(metodo):
    if not settings.TELEGRAM_BOT_TOKEN:
        raise TelegramNonConfigurato("TELEGRAM_BOT_TOKEN non configurato nel .env.")
    return f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/{metodo}"


def _chiamata(metodo, **parametri):
    dati = json.dumps(parametri).encode("utf-8")
    richiesta = urllib.request.Request(
        _url(metodo), data=dati, headers={"Content-Type": "application/json"}
    )
    try:
        with urllib.request.urlopen(richiesta, timeout=TIMEOUT_SECONDI) as risposta:
            corpo = json.loads(risposta.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        corpo = json.loads(exc.read().decode("utf-8"))
        raise RuntimeError(f"Telegram ha rifiutato la richiesta: {corpo.get('description', exc)}")
    if not corpo.get("ok"):
        raise RuntimeError(f"Risposta Telegram non ok: {corpo}")
    return corpo["result"]


def invia_messaggio(chat_id, testo):
    """Invia un messaggio di testo alla chat indicata. Solleva RuntimeError se fallisce."""
    _chiamata("sendMessage", chat_id=chat_id, text=testo)


def ottieni_aggiornamenti(offset):
    """Recupera i messaggi ricevuti dal bot a partire da `offset` (update_id + 1)."""
    return _chiamata("getUpdates", offset=offset, timeout=0)
