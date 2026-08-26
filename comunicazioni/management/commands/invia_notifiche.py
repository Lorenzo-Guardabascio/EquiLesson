"""Invia promemoria lezione e alert di scadenza via email.

Pensato per essere lanciato una volta al giorno da cron:
    0 8 * * * /path/venv/bin/python manage.py invia_notifiche

Usa NotificaInviata per non inviare due volte lo stesso avviso: se lo si
rilancia più volte nello stesso giorno (o si dimentica di rimuovere il cron
vecchio) non manda email doppie.
"""

from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from comunicazioni.models import NotificaInviata
from comunicazioni.services import invia_notifica_allievo
from lezioni.models import Partecipazione
from pacchetti.models import Pacchetto
from persone.models import Allievo

GIORNI_PREAVVISO_LEZIONE = 1
GIORNI_PREAVVISO_SCADENZE = 30


class Command(BaseCommand):
    help = "Invia via email i promemoria lezione di domani e gli alert di scadenza (certificato/tessere/pacchetto)."

    def handle(self, *args, **options):
        oggi = timezone.localdate()
        n_promemoria = self._promemoria_lezioni(oggi)
        n_scadenze = self._alert_scadenze(oggi)
        self.stdout.write(self.style.SUCCESS(
            f"Inviati {n_promemoria} promemoria lezione e {n_scadenze} alert di scadenza."
        ))

    @staticmethod
    def _invia_se_nuovo(tipo, allievo, riferimento, oggetto, corpo):
        """Invia solo se non risulta già un avviso identico registrato; ritorna True se ha inviato.

        La riga di dedupe si registra SOLO dopo un invio riuscito su almeno un
        canale (non prima): un allievo senza alcun canale disponibile oggi (né
        email né Telegram collegato) deve poter ricevere l'avviso il giorno in
        cui gliene viene attivato uno, non restare bloccato per sempre da una
        riga scritta quando non c'era modo di raggiungerlo.
        """
        già_inviato = NotificaInviata.objects.filter(
            tipo=tipo, allievo=allievo, riferimento=riferimento
        ).exists()
        if già_inviato:
            return False
        inviato = invia_notifica_allievo(oggetto, corpo, allievo)
        if inviato:
            NotificaInviata.objects.get_or_create(tipo=tipo, allievo=allievo, riferimento=riferimento)
        return inviato

    def _promemoria_lezioni(self, oggi):
        domani = oggi + timedelta(days=GIORNI_PREAVVISO_LEZIONE)
        count = 0
        partecipazioni = (
            Partecipazione.objects.filter(lezione__data=domani)
            .exclude(stato=Partecipazione.Stato.ANNULLATA)
            .select_related("lezione", "lezione__tipo_lezione", "allievo")
        )
        for p in partecipazioni:
            oggetto = f"Promemoria: lezione di domani {p.lezione.data:%d/%m}"
            corpo = (
                f"Ciao {p.allievo.nome},\n\n"
                f"ti ricordiamo la tua lezione di {p.lezione.tipo_lezione} "
                f"il {p.lezione.data:%d/%m/%Y} alle {p.lezione.ora_inizio:%H:%M}.\n\n"
                "A presto!"
            )
            if self._invia_se_nuovo(
                NotificaInviata.Tipo.PROMEMORIA_LEZIONE, p.allievo, p.lezione.data, oggetto, corpo
            ):
                count += 1
        return count

    def _alert_scadenze(self, oggi):
        limite = oggi + timedelta(days=GIORNI_PREAVVISO_SCADENZE)
        count = 0

        allievi_attivi = Allievo.objects.filter(stato=Allievo.Stato.ATTIVO)

        scadenze_allievo = [
            (
                "certificato_medico_scadenza",
                NotificaInviata.Tipo.SCADENZA_CERTIFICATO,
                "Il tuo certificato medico sta per scadere",
                "il tuo certificato medico",
            ),
            (
                "tessera_fise_scadenza",
                NotificaInviata.Tipo.SCADENZA_FISE,
                "La tua tessera FISE sta per scadere",
                "la tua tessera FISE",
            ),
            (
                "tessera_fitetrek_scadenza",
                NotificaInviata.Tipo.SCADENZA_FITETREK,
                "La tua tessera FITETREK sta per scadere",
                "la tua tessera FITETREK",
            ),
        ]
        # Nessun limite inferiore: una scadenza già passata (es. certificato scaduto
        # da un cron rimasto fermo qualche giorno) deve comunque generare un avviso,
        # non essere silenziosamente ignorata. La dedupe su NotificaInviata garantisce
        # comunque un solo invio per ciascuna data di scadenza.
        for campo, tipo, oggetto, descrizione in scadenze_allievo:
            filtro = {f"{campo}__isnull": False, f"{campo}__lte": limite}
            for allievo in allievi_attivi.filter(**filtro):
                scadenza = getattr(allievo, campo)
                corpo = (
                    f"Ciao {allievo.nome},\n\n{descrizione} scade il {scadenza:%d/%m/%Y}. "
                    "Ricordati di rinnovarlo/a per tempo.\n\nA presto!"
                )
                if self._invia_se_nuovo(tipo, allievo, scadenza, oggetto, corpo):
                    count += 1

        pacchetti = Pacchetto.objects.filter(
            stato=Pacchetto.Stato.ATTIVO, data_scadenza__lte=limite,
        ).select_related("allievo", "tipo_pacchetto")
        for pacchetto in pacchetti:
            oggetto = "Il tuo pacchetto lezioni sta per scadere"
            corpo = (
                f"Ciao {pacchetto.allievo.nome},\n\n"
                f"il tuo pacchetto {pacchetto.tipo_pacchetto.nome} ({pacchetto.lezioni_residue} lezioni "
                f"residue) scade il {pacchetto.data_scadenza:%d/%m/%Y}.\n\nA presto!"
            )
            if self._invia_se_nuovo(
                NotificaInviata.Tipo.SCADENZA_PACCHETTO, pacchetto.allievo, pacchetto.data_scadenza, oggetto, corpo
            ):
                count += 1

        return count
