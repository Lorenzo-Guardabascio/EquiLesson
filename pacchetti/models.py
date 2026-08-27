from django.db import models

from persone.models import Allievo


class TipoPacchetto(models.Model):
    """Definizione configurabile di un taglio di pacchetto (es. 4/8/12 lezioni)."""

    nome = models.CharField(max_length=100)
    numero_lezioni = models.PositiveIntegerField()
    durata_giorni = models.PositiveIntegerField(default=30)
    prezzo = models.DecimalField(
        max_digits=8, decimal_places=2, null=True, blank=True,
        help_text="Solo di riferimento/consultazione: nessuna fatturazione o incasso viene tracciato.",
    )
    prezzo_scontato_pensione = models.DecimalField(
        max_digits=8, decimal_places=2, null=True, blank=True,
        help_text="Prezzo di riferimento per i proprietari di cavalli in pensione.",
    )
    attivo = models.BooleanField(default=True)

    class Meta:
        ordering = ["numero_lezioni"]
        verbose_name = "tipo di pacchetto"
        verbose_name_plural = "tipi di pacchetto"

    def __str__(self):
        return f"{self.nome} ({self.numero_lezioni} lezioni)"


class Pacchetto(models.Model):
    """Pacchetto acquistato da un allievo: solo conteggio lezioni, niente dati economici."""

    class Stato(models.TextChoices):
        ATTIVO = "attivo", "Attivo"
        SCADUTO = "scaduto", "Scaduto"
        IN_PAUSA = "in_pausa", "In pausa"

    allievo = models.ForeignKey(Allievo, on_delete=models.CASCADE, related_name="pacchetti")
    tipo_pacchetto = models.ForeignKey(
        TipoPacchetto, on_delete=models.PROTECT, related_name="pacchetti_assegnati"
    )
    data_inizio = models.DateField()
    data_scadenza = models.DateField()
    lezioni_totali = models.PositiveIntegerField()
    stato = models.CharField(max_length=10, choices=Stato.choices, default=Stato.ATTIVO)
    note = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ["-data_inizio"]
        verbose_name = "pacchetto"
        verbose_name_plural = "pacchetti"

    def __str__(self):
        return f"{self.allievo} - {self.tipo_pacchetto} ({self.lezioni_residue} residue)"

    @property
    def lezioni_utilizzate(self):
        """Quante lezioni ha già consumato: calcolato, non un contatore salvato
        a mano né un collegamento esplicito da scegliere lezione per lezione.

        Un pacchetto è un blocco di N lezioni con una finestra di validità:
        conta come "usata" ogni lezione svolta o un'assenza (il cavallo/
        istruttore/orario erano comunque stati riservati) di quell'allievo la
        cui data cade dentro [data_inizio, data_scadenza] — non serve altro.
        Un allievo ha un solo pacchetto attivo alla volta, quindi non c'è
        ambiguità possibile su quale pacchetto "copra" una lezione.
        """
        from lezioni.models import Partecipazione

        return Partecipazione.objects.filter(
            allievo=self.allievo,
            stato__in=[Partecipazione.Stato.SVOLTA, Partecipazione.Stato.ASSENTE],
            lezione__data__gte=self.data_inizio,
            lezione__data__lte=self.data_scadenza,
        ).count()

    @property
    def lezioni_residue(self):
        """Può essere negativo: un allievo che fa una lezione in più di quelle
        pagate deve risultare "in debito" (es. -1), non azzerato a 0 come se
        fosse tutto regolare — altrimenti lo sforamento resta invisibile e
        nessuno se ne accorge finché non è tardi."""
        return self.lezioni_totali - self.lezioni_utilizzate

    @property
    def in_debito(self):
        return self.lezioni_residue < 0
