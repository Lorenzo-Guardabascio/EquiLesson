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
        a mano. Prima era un campo che nessuna parte del codice aggiornava mai
        — si poteva collegare un pacchetto a una partecipazione e il conteggio
        non si muoveva di una virgola. Contando dalle partecipazioni vere non
        può più disallinearsi dalla realtà: conta come "usata" una lezione
        svolta o un'assenza (il cavallo/istruttore/orario erano comunque
        stati riservati), non una lezione ancora prevista o annullata.
        """
        from lezioni.models import Partecipazione

        return self.partecipazioni.filter(
            stato__in=[Partecipazione.Stato.SVOLTA, Partecipazione.Stato.ASSENTE]
        ).count()

    @property
    def lezioni_residue(self):
        return max(self.lezioni_totali - self.lezioni_utilizzate, 0)
