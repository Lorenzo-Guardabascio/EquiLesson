from django.db import models

from cavalli.models import Cavallo
from persone.models import Allievo, Istruttore


class Campo(models.Model):
    """Struttura/campo del centro (es. 'Grande', 'Piccolo')."""

    nome = models.CharField(max_length=50)
    note = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ["nome"]
        verbose_name = "campo"
        verbose_name_plural = "campi"

    def __str__(self):
        return self.nome


class TipoLezione(models.Model):
    """Tipo di lezione, configurabile (individuale, gruppo, salto, dressage, ...)."""

    nome = models.CharField(max_length=100)
    durata_default_minuti = models.PositiveIntegerField(default=60)
    capienza_max = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="Capienza massima",
        help_text=(
            "Numero massimo di allievi per una lezione di questo tipo. Lasciare "
            "vuoto per nessun limite. Usata solo per la prenotazione autonoma "
            "degli allievi dal portale — l'admin può sempre aggiungere partecipanti "
            "oltre il limite dal form lezione."
        ),
    )
    attivo = models.BooleanField(default=True)

    class Meta:
        ordering = ["nome"]
        verbose_name = "tipo di lezione"
        verbose_name_plural = "tipi di lezione"

    def __str__(self):
        return self.nome


class Lezione(models.Model):
    """Una lezione pianificata: l'evento in calendario, non ancora legato al singolo allievo."""

    class Stato(models.TextChoices):
        PRENOTATA = "prenotata", "Prenotata"
        CONFERMATA = "confermata", "Confermata"
        SVOLTA = "svolta", "Svolta"
        ANNULLATA = "annullata", "Annullata"

    data = models.DateField()
    ora_inizio = models.TimeField()
    ora_fine = models.TimeField()
    tipo_lezione = models.ForeignKey(TipoLezione, on_delete=models.PROTECT, related_name="lezioni")
    istruttore = models.ForeignKey(
        Istruttore, on_delete=models.SET_NULL, null=True, blank=True, related_name="lezioni"
    )
    campo = models.ForeignKey(
        Campo, on_delete=models.SET_NULL, null=True, blank=True, related_name="lezioni"
    )
    stato = models.CharField(max_length=15, choices=Stato.choices, default=Stato.PRENOTATA)
    note = models.TextField(blank=True)

    allievi = models.ManyToManyField(Allievo, through="Partecipazione", related_name="lezioni")

    class Meta:
        ordering = ["data", "ora_inizio"]
        verbose_name = "lezione"
        verbose_name_plural = "lezioni"

    def __str__(self):
        return f"{self.tipo_lezione} - {self.data} {self.ora_inizio:%H:%M}"


class Partecipazione(models.Model):
    """Collega un allievo a una lezione con il cavallo assegnato per quella lezione.

    Serve come modello a sé (invece di FK diretti sulla Lezione) perché in una
    lezione di gruppo ogni allievo può montare un cavallo diverso.
    """

    class Stato(models.TextChoices):
        PREVISTA = "prevista", "Prevista"
        SVOLTA = "svolta", "Svolta"
        ASSENTE = "assente", "Assente"
        ANNULLATA = "annullata", "Annullata"

    lezione = models.ForeignKey(Lezione, on_delete=models.CASCADE, related_name="partecipazioni")
    allievo = models.ForeignKey(Allievo, on_delete=models.CASCADE, related_name="partecipazioni")
    cavallo = models.ForeignKey(
        Cavallo, on_delete=models.SET_NULL, null=True, blank=True, related_name="partecipazioni"
    )
    stato = models.CharField(max_length=15, choices=Stato.choices, default=Stato.PREVISTA)
    note = models.CharField(max_length=255, blank=True)

    class Meta:
        unique_together = ("lezione", "allievo")
        ordering = ["lezione"]
        verbose_name = "partecipazione"
        verbose_name_plural = "partecipazioni"

    def __str__(self):
        return f"{self.allievo} @ {self.lezione}"
