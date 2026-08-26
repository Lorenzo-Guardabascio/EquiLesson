from django.db import models

from persone.models import Proprietario


class Cavallo(models.Model):
    class Tipo(models.TextChoices):
        SCUOLA = "scuola", "Cavallo di scuola"
        PENSIONE = "pensione", "Cavallo in pensione"

    class LivelloImpiego(models.TextChoices):
        PRINCIPIANTI = "principianti", "Principianti"
        INTERMEDIO = "intermedio", "Intermedio"
        AVANZATO = "avanzato", "Avanzato"
        RIPOSO = "riposo", "A riposo"

    nome = models.CharField(max_length=100)
    razza = models.CharField(max_length=100, blank=True)
    data_nascita = models.DateField(null=True, blank=True)
    sesso = models.CharField(max_length=20, blank=True)
    microchip = models.CharField(max_length=50, blank=True)

    tipo = models.CharField(max_length=10, choices=Tipo.choices, default=Tipo.SCUOLA)
    proprietario = models.ForeignKey(
        Proprietario,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="cavalli",
        help_text="Solo per cavalli in pensione.",
    )

    livello_impiego = models.CharField(
        max_length=20, choices=LivelloImpiego.choices, default=LivelloImpiego.INTERMEDIO
    )
    disponibile = models.BooleanField(default=True)
    note_disponibilita = models.CharField(max_length=255, blank=True)

    box = models.CharField(max_length=50, blank=True, help_text="Solo per cavalli in pensione.")
    note_sanitarie = models.TextField(
        blank=True, help_text="Vaccinazioni, sverminazioni, ferrature, veterinario..."
    )

    class Meta:
        ordering = ["nome"]
        verbose_name = "cavallo"
        verbose_name_plural = "cavalli"

    def __str__(self):
        return self.nome
