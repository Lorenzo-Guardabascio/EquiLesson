"""Popola il database con dati di esempio (placeholder), utili solo per provare l'app.

Uso:
    python manage.py carica_dati_demo

È sicuro rilanciarlo più volte: usa get_or_create sulle chiavi principali,
quindi non duplica gli stessi record di esempio.
"""

from datetime import date, timedelta

from django.core.management.base import BaseCommand

from cavalli.models import Cavallo
from lezioni.models import Campo, Lezione, Partecipazione, TipoLezione
from pacchetti.models import Pacchetto, TipoPacchetto
from persone.models import Allievo, Istruttore, Proprietario, Tutore


class Command(BaseCommand):
    help = "Carica dati di esempio (placeholder) per provare il gestionale."

    def handle(self, *args, **options):
        oggi = date.today()

        # --- Istruttori (placeholder: nella realtà sono anche i proprietari) ---
        istruttore_1, _ = Istruttore.objects.get_or_create(
            nome="Marco", cognome="Rossi",
            defaults=dict(telefono="333 1234567", email="marco.rossi@example.com"),
        )
        istruttore_2, _ = Istruttore.objects.get_or_create(
            nome="Giulia", cognome="Bianchi",
            defaults=dict(telefono="333 7654321", email="giulia.bianchi@example.com"),
        )

        # --- Tutori ---
        tutore_1, _ = Tutore.objects.get_or_create(
            nome="Anna", cognome="Verdi",
            defaults=dict(relazione=Tutore.Relazione.MADRE, telefono="347 1112222"),
        )
        tutore_2, _ = Tutore.objects.get_or_create(
            nome="Luca", cognome="Neri",
            defaults=dict(relazione=Tutore.Relazione.PADRE, telefono="347 3334444"),
        )

        # --- Proprietari cavalli in pensione ---
        prop_1, _ = Proprietario.objects.get_or_create(
            nome="Roberto", cognome="Galli", defaults=dict(telefono="335 5556666")
        )
        prop_2, _ = Proprietario.objects.get_or_create(
            nome="Francesca", cognome="Lombardi", defaults=dict(telefono="335 7778888")
        )

        # --- Cavalli: 8 di scuola + 2 in pensione ---
        cavalli_scuola = ["Aron", "Luna", "Ombra", "Freccia", "Stella", "Diamante", "Perla", "Vento"]
        cavalli = {}
        for nome in cavalli_scuola:
            cavalli[nome], _ = Cavallo.objects.get_or_create(
                nome=nome,
                defaults=dict(
                    tipo=Cavallo.Tipo.SCUOLA,
                    livello_impiego=Cavallo.LivelloImpiego.INTERMEDIO,
                    razza="Sella Italiano",
                ),
            )
        cavalli["Zefiro"], _ = Cavallo.objects.get_or_create(
            nome="Zefiro",
            defaults=dict(tipo=Cavallo.Tipo.PENSIONE, proprietario=prop_1, box="Box 1"),
        )
        cavalli["Nuvola"], _ = Cavallo.objects.get_or_create(
            nome="Nuvola",
            defaults=dict(tipo=Cavallo.Tipo.PENSIONE, proprietario=prop_2, box="Box 2"),
        )

        # --- Campi ---
        campo_grande, _ = Campo.objects.get_or_create(nome="Campo Grande")
        campo_piccolo, _ = Campo.objects.get_or_create(nome="Campo Piccolo")

        # --- Tipi di lezione ---
        nomi_tipi_lezione = [
            "Individuale", "Gruppo", "Salto ostacoli", "Dressage",
            "Passeggiata", "Ippoterapia", "Battesimo della sella", "Lavoro da terra",
        ]
        tipi_lezione = {}
        for nome in nomi_tipi_lezione:
            tipi_lezione[nome], _ = TipoLezione.objects.get_or_create(nome=nome)

        # --- Tipi di pacchetto (prezzi puramente di esempio, da correggere) ---
        pacchetto_4, _ = TipoPacchetto.objects.get_or_create(
            nome="Pacchetto 4 lezioni",
            defaults=dict(numero_lezioni=4, durata_giorni=30, prezzo=80, prezzo_scontato_pensione=70),
        )
        pacchetto_8, _ = TipoPacchetto.objects.get_or_create(
            nome="Pacchetto 8 lezioni",
            defaults=dict(numero_lezioni=8, durata_giorni=30, prezzo=150, prezzo_scontato_pensione=130),
        )
        pacchetto_12, _ = TipoPacchetto.objects.get_or_create(
            nome="Pacchetto 12 lezioni",
            defaults=dict(numero_lezioni=12, durata_giorni=30, prezzo=210, prezzo_scontato_pensione=180),
        )

        # --- Allievi ---
        allievi_dati = [
            dict(nome="Sofia", cognome="Ricci", data_nascita=date(2016, 4, 12),
                 propensione="Salto ostacoli", tutori=[tutore_1],
                 certificato_medico_tipo=Allievo.TipoCertificato.NON_AGONISTICO,
                 certificato_medico_scadenza=oggi + timedelta(days=200)),
            dict(nome="Marco", cognome="Gallo", data_nascita=date(2010, 9, 3),
                 propensione="Dressage", tutori=[tutore_2],
                 certificato_medico_tipo=Allievo.TipoCertificato.NON_AGONISTICO,
                 certificato_medico_scadenza=oggi + timedelta(days=15)),  # in scadenza a breve
            dict(nome="Elena", cognome="Conti", data_nascita=date(1990, 6, 20),
                 propensione="Passeggiata",
                 certificato_medico_tipo=Allievo.TipoCertificato.NON_AGONISTICO,
                 certificato_medico_scadenza=oggi + timedelta(days=300)),
            dict(nome="Davide", cognome="Ferrari", data_nascita=date(2002, 1, 15),
                 propensione="Salto ostacoli - agonista",
                 certificato_medico_tipo=Allievo.TipoCertificato.AGONISTICO,
                 certificato_medico_scadenza=oggi + timedelta(days=100),
                 tessera_fise_numero="FISE123456", tessera_fise_scadenza=oggi + timedelta(days=100)),
            dict(nome="Giorgia", cognome="Villa", data_nascita=date(2018, 11, 5),
                 propensione="Ippoterapia", tutori=[tutore_1],
                 note_particolari="Ippoterapia - lieve disabilità motoria, seguita dall'istruttore Giulia.",
                 certificato_medico_tipo=Allievo.TipoCertificato.NON_AGONISTICO,
                 certificato_medico_scadenza=oggi + timedelta(days=250)),
            dict(nome="Alessandro", cognome="Moretti", data_nascita=date(1985, 3, 30),
                 propensione="Lavoro da terra",
                 certificato_medico_tipo=Allievo.TipoCertificato.NON_AGONISTICO,
                 certificato_medico_scadenza=oggi - timedelta(days=10)),  # scaduto, di proposito
            dict(nome="Chiara", cognome="Fontana", data_nascita=date(2013, 7, 22),
                 propensione="Gruppo", tutori=[tutore_2],
                 certificato_medico_tipo=Allievo.TipoCertificato.NON_AGONISTICO,
                 certificato_medico_scadenza=oggi + timedelta(days=180)),
            dict(nome="Paolo", cognome="Serra", data_nascita=date(1995, 12, 1),
                 propensione="Dressage", stato=Allievo.Stato.SOSPESO,
                 certificato_medico_tipo=Allievo.TipoCertificato.NON_AGONISTICO,
                 certificato_medico_scadenza=oggi + timedelta(days=60)),
        ]

        allievi = {}
        for dati in allievi_dati:
            tutori = dati.pop("tutori", [])
            allievo, created = Allievo.objects.get_or_create(
                nome=dati["nome"], cognome=dati["cognome"],
                defaults={**dati, "consenso_privacy": True, "consenso_foto_video": True},
            )
            if created and tutori:
                allievo.tutori.set(tutori)
            allievi[f"{dati['nome']} {dati['cognome']}"] = allievo

        # --- Pacchetti assegnati ad alcuni allievi ---
        # lezioni_utilizzate non si imposta più a mano né si collega a mano a
        # una partecipazione: si calcola da sola dalle lezioni svolte/assenti
        # di quell'allievo la cui data cade dentro data_inizio/data_scadenza
        # (vedi Pacchetto.lezioni_utilizzate) — qui sotto basta che le date
        # coincidano con quelle delle lezioni create più sotto.
        Pacchetto.objects.get_or_create(
            allievo=allievi["Sofia Ricci"], tipo_pacchetto=pacchetto_8,
            defaults=dict(data_inizio=oggi - timedelta(days=5), data_scadenza=oggi + timedelta(days=25),
                          lezioni_totali=8),
        )
        Pacchetto.objects.get_or_create(
            allievo=allievi["Marco Gallo"], tipo_pacchetto=pacchetto_4,
            defaults=dict(data_inizio=oggi - timedelta(days=20), data_scadenza=oggi + timedelta(days=10),
                          lezioni_totali=4),
        )
        Pacchetto.objects.get_or_create(
            allievo=allievi["Elena Conti"], tipo_pacchetto=pacchetto_12,
            defaults=dict(data_inizio=oggi - timedelta(days=2), data_scadenza=oggi + timedelta(days=28),
                          lezioni_totali=12),
        )

        # --- Qualche lezione, passata e futura ---
        lezione_passata, _ = Lezione.objects.get_or_create(
            data=oggi - timedelta(days=2), ora_inizio="16:00", ora_fine="17:00",
            tipo_lezione=tipi_lezione["Individuale"], istruttore=istruttore_1, campo=campo_piccolo,
            defaults=dict(stato=Lezione.Stato.SVOLTA),
        )
        Partecipazione.objects.get_or_create(
            lezione=lezione_passata, allievo=allievi["Sofia Ricci"],
            defaults=dict(cavallo=cavalli["Luna"], stato=Partecipazione.Stato.SVOLTA),
        )

        lezione_gruppo, _ = Lezione.objects.get_or_create(
            data=oggi + timedelta(days=1), ora_inizio="15:00", ora_fine="16:00",
            tipo_lezione=tipi_lezione["Gruppo"], istruttore=istruttore_2, campo=campo_grande,
            defaults=dict(stato=Lezione.Stato.CONFERMATA),
        )
        Partecipazione.objects.get_or_create(
            lezione=lezione_gruppo, allievo=allievi["Chiara Fontana"],
            defaults=dict(cavallo=cavalli["Perla"]),
        )
        Partecipazione.objects.get_or_create(
            lezione=lezione_gruppo, allievo=allievi["Marco Gallo"],
            defaults=dict(cavallo=cavalli["Ombra"]),
        )

        lezione_ippoterapia, _ = Lezione.objects.get_or_create(
            data=oggi + timedelta(days=3), ora_inizio="10:00", ora_fine="10:45",
            tipo_lezione=tipi_lezione["Ippoterapia"], istruttore=istruttore_2, campo=campo_piccolo,
            defaults=dict(stato=Lezione.Stato.PRENOTATA),
        )
        Partecipazione.objects.get_or_create(
            lezione=lezione_ippoterapia, allievo=allievi["Giorgia Villa"],
            defaults=dict(cavallo=cavalli["Vento"]),
        )

        self.stdout.write(self.style.SUCCESS(
            "Dati di esempio caricati: "
            f"{Allievo.objects.count()} allievi, {Cavallo.objects.count()} cavalli, "
            f"{Istruttore.objects.count()} istruttori, {Lezione.objects.count()} lezioni, "
            f"{Pacchetto.objects.count()} pacchetti."
        ))
