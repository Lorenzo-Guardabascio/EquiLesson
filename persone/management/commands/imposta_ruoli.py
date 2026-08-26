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

from persone.models import Istruttore

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
    help = "Crea i gruppi Istruttori/Allievi con i permessi di base e account demo per gli istruttori."

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

        # Gruppo Allievi: segnaposto, nessun permesso admin.
        # L'accesso vero sarà una vista dedicata di sola lettura, non l'admin di Django.
        Group.objects.get_or_create(name="Allievi")

        self.stdout.write(self.style.SUCCESS(
            f"Gruppo 'Istruttori' impostato con {istruttori_group.permissions.count()} permessi."
        ))
        self.stdout.write("Gruppo 'Allievi' creato (senza accesso admin, in attesa del portale dedicato).")

        # Collega un account di accesso a ogni istruttore demo che non ce l'ha già.
        credenziali = []
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
            credenziali.append((username, password))

        if credenziali:
            self.stdout.write(self.style.SUCCESS("Account istruttore creati:"))
            for username, password in credenziali:
                self.stdout.write(f"  {username} / {password}")
        else:
            self.stdout.write("Nessun nuovo account istruttore da creare (già collegati).")
