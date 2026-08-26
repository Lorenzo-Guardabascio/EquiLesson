"""Crea i gruppi di permessi (Istruttori, Allievi) e collega account di test agli istruttori demo.

Uso:
    python manage.py imposta_ruoli

Sicuro da rilanciare più volte.
"""

import secrets
import string

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.core.management.base import BaseCommand

from persone.models import Allievo, Istruttore

# Gli istruttori possono vedere e gestire lezioni/partecipazioni...
ISTRUTTORI_GESTIONE = [
    ("lezioni", "lezione"),
    ("lezioni", "partecipazione"),
]
# ...ma solo consultare il resto (allievi, cavalli, pacchetti, configurazioni).
ISTRUTTORI_SOLA_LETTURA = [
    ("persone", "allievo"),
    ("cavalli", "cavallo"),
    ("lezioni", "campo"),
    ("lezioni", "tipolezione"),
    ("pacchetti", "pacchetto"),
    ("pacchetti", "tipopacchetto"),
]


def genera_password():
    alfabeto = string.ascii_letters + string.digits
    return "".join(secrets.choice(alfabeto) for _ in range(16))


class Command(BaseCommand):
    help = (
        "Crea i gruppi Istruttori/Allievi con i permessi di base e gli account di accesso "
        "per istruttori e allievi che non ne hanno ancora uno."
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

        # Gruppo Allievi: nessun permesso admin (il gruppo esiste solo per riconoscere il
        # ruolo). L'accesso vero è il portale dedicato di sola lettura, non l'admin di Django.
        allievi_group, _ = Group.objects.get_or_create(name="Allievi")

        self.stdout.write(self.style.SUCCESS(
            f"Gruppo 'Istruttori' impostato con {istruttori_group.permissions.count()} permessi."
        ))
        self.stdout.write("Gruppo 'Allievi' impostato (senza accesso admin, solo portale dedicato).")

        # Collega un account di accesso a ogni istruttore demo che non ce l'ha già.
        credenziali_istruttori = []
        for istruttore in Istruttore.objects.filter(utente__isnull=True):
            username = f"{istruttore.nome}.{istruttore.cognome}".lower().replace(" ", "")
            if User.objects.filter(username=username).exists():
                continue
            password = genera_password()
            user = User.objects.create_user(
                username=username,
                email=istruttore.email,
                password=password,
                first_name=istruttore.nome,
                last_name=istruttore.cognome,
                is_staff=True,
            )
            user.groups.add(istruttori_group)
            istruttore.utente = user
            istruttore.save(update_fields=["utente"])
            credenziali_istruttori.append((username, password))

        if credenziali_istruttori:
            self.stdout.write(self.style.SUCCESS("Account istruttore creati:"))
            for username, password in credenziali_istruttori:
                self.stdout.write(f"  {username} / {password}")
        else:
            self.stdout.write("Nessun nuovo account istruttore da creare (già collegati).")

        # Collega un account di accesso (solo portale, mai staff) a ogni allievo attivo
        # che non ce l'ha già.
        credenziali_allievi = []
        for allievo in Allievo.objects.filter(utente__isnull=True, stato=Allievo.Stato.ATTIVO):
            username = f"{allievo.nome}.{allievo.cognome}".lower().replace(" ", "")
            if User.objects.filter(username=username).exists():
                continue
            password = genera_password()
            user = User.objects.create_user(
                username=username,
                email=allievo.email,
                password=password,
                first_name=allievo.nome,
                last_name=allievo.cognome,
                is_staff=False,
            )
            user.groups.add(allievi_group)
            allievo.utente = user
            allievo.save(update_fields=["utente"])
            credenziali_allievi.append((username, password))

        if credenziali_allievi:
            self.stdout.write(self.style.SUCCESS("Account allievo (portale) creati:"))
            for username, password in credenziali_allievi:
                self.stdout.write(f"  {username} / {password}")
        else:
            self.stdout.write("Nessun nuovo account allievo da creare (già collegati o nessun allievo attivo).")
