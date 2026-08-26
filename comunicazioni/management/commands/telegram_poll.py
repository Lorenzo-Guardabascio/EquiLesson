"""Controlla i messaggi ricevuti dal bot Telegram e collega gli account /link.

Pensato per girare spesso da cron (es. ogni 2 minuti), non una volta al
giorno come `invia_notifiche`: un allievo che ha appena generato un codice
dal portale si aspetta un collegamento quasi immediato.

    */2 * * * * /path/venv/bin/python /path/manage.py telegram_poll >> /path/logs/telegram.log 2>&1

Non fa nulla (esce subito) se TELEGRAM_BOT_TOKEN non è configurato, così è
sicuro tenerlo nel cron anche prima di aver creato un bot.
"""

import re

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone

from comunicazioni.canali import telegram
from comunicazioni.models import TelegramLink, TelegramPollState

PATTERN_LINK = re.compile(r"^/link[@\w]*\s+(\S+)", re.IGNORECASE)


class Command(BaseCommand):
    help = "Legge i messaggi Telegram in arrivo e collega gli account allievo che inviano /link <codice>."

    def handle(self, *args, **options):
        if not settings.TELEGRAM_BOT_TOKEN:
            self.stdout.write("TELEGRAM_BOT_TOKEN non configurato: nulla da fare.")
            return

        stato = TelegramPollState.get()
        aggiornamenti = telegram.ottieni_aggiornamenti(offset=stato.ultimo_update_id + 1)

        n_collegati = 0
        ultimo_id_visto = stato.ultimo_update_id

        for aggiornamento in aggiornamenti:
            ultimo_id_visto = max(ultimo_id_visto, aggiornamento["update_id"])
            messaggio = aggiornamento.get("message")
            if not messaggio or "text" not in messaggio:
                continue

            chat_id = str(messaggio["chat"]["id"])
            testo = messaggio["text"].strip()
            match = PATTERN_LINK.match(testo)

            if match:
                codice = match.group(1).strip()
                link = TelegramLink.objects.filter(codice_collegamento=codice).exclude(codice_collegamento="").first()
                if link:
                    link.chat_id = chat_id
                    link.collegato_il = timezone.now()
                    link.codice_collegamento = ""
                    link.save(update_fields=["chat_id", "collegato_il", "codice_collegamento"])
                    n_collegati += 1
                    telegram.invia_messaggio(
                        chat_id,
                        f"Collegamento riuscito! Da ora riceverai qui le notifiche di {link.allievo.nome}.",
                    )
                else:
                    telegram.invia_messaggio(
                        chat_id,
                        "Codice non riconosciuto o già usato. Genera un nuovo codice dal tuo portale EquiLesson e riprova.",
                    )
            elif testo.lower().startswith("/start"):
                telegram.invia_messaggio(
                    chat_id,
                    "Ciao! Per collegare il tuo account genera un codice dal portale EquiLesson "
                    "(sezione Telegram) e invialo qui scrivendo: /link CODICE",
                )

        if ultimo_id_visto != stato.ultimo_update_id:
            stato.ultimo_update_id = ultimo_id_visto
            stato.save(update_fields=["ultimo_update_id"])

        self.stdout.write(self.style.SUCCESS(
            f"{len(aggiornamenti)} aggiornamenti letti, {n_collegati} nuovi collegamenti."
        ))
