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
        blank=True,
        help_text="Note libere aggiuntive. Le scadenze da tenere sotto controllo vanno in "
        "'Scadenze sanitarie' qui sotto, non qui: solo così generano un promemoria automatico.",
    )

    class Meta:
        ordering = ["nome"]
        verbose_name = "cavallo"
        verbose_name_plural = "cavalli"

    def __str__(self):
        return self.nome


class ScadenzaSanitaria(models.Model):
    """Un evento sanitario datato del cavallo (prossima vaccinazione, ferratura...).

    A differenza di `note_sanitarie` (testo libero) questa ha una data
    strutturata: solo così il comando `invia_notifiche` può generare un
    promemoria automatico invece di richiedere un controllo manuale.
    """

    class Tipo(models.TextChoices):
        VACCINAZIONE = "vaccinazione", "Vaccinazione"
        SVERMINAZIONE = "sverminazione", "Sverminazione"
        FERRATURA = "ferratura", "Ferratura"
        VISITA_VETERINARIA = "visita_veterinaria", "Visita veterinaria"
        ALTRO = "altro", "Altro"

    cavallo = models.ForeignKey(Cavallo, on_delete=models.CASCADE, related_name="scadenze_sanitarie")
    tipo = models.CharField(max_length=30, choices=Tipo.choices, default=Tipo.ALTRO)
    data_scadenza = models.DateField(verbose_name="Prossima scadenza")
    note = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ["data_scadenza"]
        verbose_name = "scadenza sanitaria"
        verbose_name_plural = "scadenze sanitarie"

    def __str__(self):
        return f"{self.get_tipo_display()} - {self.cavallo} ({self.data_scadenza:%d/%m/%Y})"
