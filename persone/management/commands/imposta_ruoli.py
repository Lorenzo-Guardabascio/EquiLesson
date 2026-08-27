"""Crea i gruppi di permessi e gli account di accesso mancanti per istruttori,
allievi attivi e proprietari di cavalli in pensione.

Uso:
    python manage.py imposta_ruoli

Sicuro da rilanciare più volte.
"""

import secrets
import string

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.core.management.base import BaseCommand

from persone.models import Allievo, Istruttore, Proprietario

# Le lezioni/partecipazioni si gestiscono SOLO dal form custom in /lezioni/
# (che richiede solo is_staff, non un permesso specifico) — l'admin di
# Django su questi due modelli è sola consultazione per chiunque (vedi
# lezioni.admin.SolaConsultazioneMixin), quindi anche gli istruttori hanno
# qui solo il permesso di vedere, mai di scrivere.
ISTRUTTORI_GESTIONE = []
ISTRUTTORI_SOLA_LETTURA = [
    ("persone", "allievo"),
    ("cavalli", "cavallo"),
    ("lezioni", "lezione"),
    ("lezioni", "partecipazione"),
    ("lezioni", "campo"),
    ("lezioni", "tipolezione"),
    ("pacchetti", "pacchetto"),
    ("pacchetti", "tipopacchetto"),
]

# La segreteria gestisce tutto il resto dal frontend (vedi core.gestione e
# core.gestione_config.REGISTRO — sono apposta le stesse app/model label
# usate lì): add/change/delete/view su tutta l'anagrafica e la
# configurazione. Le lezioni non servono qui: is_staff basta già per il
# form custom, che non controlla permessi granulari.
SEGRETERIA_GESTIONE = [
    ("persone", "allievo"),
    ("persone", "tutore"),
    ("persone", "istruttore"),
    ("persone", "proprietario"),
    ("persone", "documento"),
    ("cavalli", "cavallo"),
    ("cavalli", "scadenzasanitaria"),
    ("pacchetti", "pacchetto"),
    ("pacchetti", "tipopacchetto"),
    ("lezioni", "campo"),
    ("lezioni", "tipolezione"),
    ("comunicazioni", "comunicazione"),
]
# Sola lettura anche per la segreteria: sono log di sistema (vedi
# comunicazioni/views.py e admin.py), non anagrafica da modificare a mano.
SEGRETERIA_SOLA_LETTURA = [
    ("comunicazioni", "notificainviata"),
    ("comunicazioni", "telegramlink"),
]


def genera_password():
    alfabeto = string.ascii_letters + string.digits
    return "".join(secrets.choice(alfabeto) for _ in range(16))


class Command(BaseCommand):
    help = (
        "Crea i gruppi Istruttori/Segreteria/Allievi/Proprietari con i permessi di base "
        "e gli account di accesso mancanti per istruttori, allievi attivi e proprietari."
    )

    def handle(self, *args, **options):
        User = get_user_model()

        istruttori_group, _ = Group.objects.get_or_create(name="Istruttori")
        permessi = []
        for app_label, model in ISTRUTTORI_GESTIONE:
            for azione in ["view", "add", "change"]:
                permessi.append(Permission.objects.get(
                    codename=f"{azione}_{model}", content_type__app_label=app_label
                ))
        for app_label, model in ISTRUTTORI_SOLA_LETTURA:
            permessi.append(Permission.objects.get(
                codename=f"view_{model}", content_type__app_label=app_label
            ))
        istruttori_group.permissions.set(permessi)
        self.stdout.write(self.style.SUCCESS(
            f"Gruppo 'Istruttori' impostato con {istruttori_group.permissions.count()} permessi."
        ))

        segreteria_group, _ = Group.objects.get_or_create(name="Segreteria")
        permessi_segreteria = []
        for app_label, model in SEGRETERIA_GESTIONE:
            for azione in ["view", "add", "change", "delete"]:
                permessi_segreteria.append(Permission.objects.get(
                    codename=f"{azione}_{model}", content_type__app_label=app_label
                ))
        for app_label, model in SEGRETERIA_SOLA_LETTURA:
            permessi_segreteria.append(Permission.objects.get(
                codename=f"view_{model}", content_type__app_label=app_label
            ))
        permessi_segreteria.append(
            Permission.objects.get(codename="change_impostazioni", content_type__app_label="core")
        )
        segreteria_group.permissions.set(permessi_segreteria)
        self.stdout.write(self.style.SUCCESS(
            f"Gruppo 'Segreteria' impostato con {segreteria_group.permissions.count()} permessi. "
            "Nessun account creato automaticamente: la segreteria non ha un modello anagrafico "
            "proprio (a differenza di istruttori/allievi/proprietari) — il sistemista crea gli "
            "account dall'admin tecnico (is_staff attivo, gruppo 'Segreteria')."
        ))

        # Allievi e Proprietari: nessun permesso admin (i gruppi esistono solo per
        # riconoscere il ruolo). L'accesso vero sono i portali dedicati di sola
        # lettura, non l'admin di Django.
        allievi_group, _ = Group.objects.get_or_create(name="Allievi")
        proprietari_group, _ = Group.objects.get_or_create(name="Proprietari")
        self.stdout.write("Gruppi 'Allievi' e 'Proprietari' impostati (senza accesso admin, solo portale dedicato).")

        self._crea_account_mancanti(
            User, Istruttore.objects.filter(utente__isnull=True),
            gruppo=istruttori_group, is_staff=True, etichetta="istruttore",
        )
        self._crea_account_mancanti(
            User, Allievo.objects.filter(utente__isnull=True, stato=Allievo.Stato.ATTIVO),
            gruppo=allievi_group, is_staff=False, etichetta="allievo",
        )
        self._crea_account_mancanti(
            User, Proprietario.objects.filter(utente__isnull=True),
            gruppo=proprietari_group, is_staff=False, etichetta="proprietario",
        )

    def _crea_account_mancanti(self, User, persone_senza_account, *, gruppo, is_staff, etichetta):
        """Crea un login per ogni persona del queryset che non ne ha ancora uno.

        Le tre categorie (istruttori/allievi/proprietari) condividono la stessa
        forma di anagrafica (nome, cognome, email, campo `utente`) quindi la
        stessa logica di creazione account basta per tutte e tre.
        """
        credenziali = []
        for persona in persone_senza_account:
            username = f"{persona.nome}.{persona.cognome}".lower().replace(" ", "")
            if User.objects.filter(username=username).exists():
                continue
            password = genera_password()
            user = User.objects.create_user(
                username=username,
                email=persona.email,
                password=password,
                first_name=persona.nome,
                last_name=persona.cognome,
                is_staff=is_staff,
            )
            user.groups.add(gruppo)
            persona.utente = user
            persona.save(update_fields=["utente"])
            credenziali.append((username, password))

        if credenziali:
            self.stdout.write(self.style.SUCCESS(f"Account {etichetta} creati:"))
            for username, password in credenziali:
                self.stdout.write(f"  {username} / {password}")
        else:
            self.stdout.write(f"Nessun nuovo account {etichetta} da creare (già collegati o nessuno da collegare).")
