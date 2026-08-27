from datetime import date

from django.conf import settings
from django.db import models

from .validators import valida_dimensione_documento, valida_tipo_documento


class Tutore(models.Model):
    """Genitore/tutore di un allievo minorenne."""

    class Relazione(models.TextChoices):
        MADRE = "madre", "Madre"
        PADRE = "padre", "Padre"
        ALTRO = "altro", "Altro"

    nome = models.CharField(max_length=100)
    cognome = models.CharField(max_length=100)
    relazione = models.CharField(max_length=10, choices=Relazione.choices, default=Relazione.ALTRO)
    telefono = models.CharField(max_length=30, blank=True)
    email = models.EmailField(blank=True)

    class Meta:
        ordering = ["cognome", "nome"]
        verbose_name = "tutore"
        verbose_name_plural = "tutori"

    def __str__(self):
        return f"{self.nome} {self.cognome}"


class Proprietario(models.Model):
    """Proprietario di un cavallo tenuto in pensione (non di scuola)."""

    utente = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="proprietario",
        help_text="Account per il portale di sola lettura sul proprio cavallo, se attivato.",
    )
    nome = models.CharField(max_length=100)
    cognome = models.CharField(max_length=100)
    telefono = models.CharField(max_length=30, blank=True)
    email = models.EmailField(blank=True)

    class Meta:
        ordering = ["cognome", "nome"]
        verbose_name = "proprietario"
        verbose_name_plural = "proprietari"

    def __str__(self):
        return f"{self.nome} {self.cognome}"


class Istruttore(models.Model):
    utente = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="istruttore",
        help_text="Account di accesso collegato, se ha un login proprio.",
    )
    nome = models.CharField(max_length=100)
    cognome = models.CharField(max_length=100)
    telefono = models.CharField(max_length=30, blank=True)
    email = models.EmailField(blank=True)
    note_disponibilita = models.TextField(blank=True)
    attivo = models.BooleanField(default=True)

    class Meta:
        ordering = ["cognome", "nome"]
        verbose_name = "istruttore"
        verbose_name_plural = "istruttori"

    def __str__(self):
        return f"{self.nome} {self.cognome}"


class Allievo(models.Model):
    class Stato(models.TextChoices):
        ATTIVO = "attivo", "Attivo"
        SOSPESO = "sospeso", "Sospeso"
        EX = "ex", "Ex allievo"

    class TipoCertificato(models.TextChoices):
        NON_AGONISTICO = "non_agonistico", "Non agonistico"
        AGONISTICO = "agonistico", "Agonistico"

    utente = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="allievo",
        help_text="Account per il portale di sola lettura, se attivato.",
    )

    nome = models.CharField(max_length=100)
    cognome = models.CharField(max_length=100)
    data_nascita = models.DateField()
    codice_fiscale = models.CharField(max_length=16, blank=True)
    telefono = models.CharField(max_length=30, blank=True)
    email = models.EmailField(blank=True)
    indirizzo = models.CharField(max_length=255, blank=True)

    tutori = models.ManyToManyField(Tutore, blank=True, related_name="allievi")

    stato = models.CharField(max_length=10, choices=Stato.choices, default=Stato.ATTIVO)

    certificato_medico_tipo = models.CharField(
        max_length=20, choices=TipoCertificato.choices, blank=True
    )
    certificato_medico_scadenza = models.DateField(null=True, blank=True)

    tessera_fise_numero = models.CharField("N. tessera FISE", max_length=50, blank=True)
    tessera_fise_scadenza = models.DateField("Scadenza tessera FISE", null=True, blank=True)
    tessera_fitetrek_numero = models.CharField("N. tessera FITETREK", max_length=50, blank=True)
    tessera_fitetrek_scadenza = models.DateField("Scadenza tessera FITETREK", null=True, blank=True)

    consenso_privacy = models.BooleanField(default=False)
    consenso_foto_video = models.BooleanField(default=False)

    propensione = models.CharField(
        max_length=100,
        blank=True,
        help_text="Verso cosa punta l'allievo: salto, dressage, passeggiata, ecc.",
    )
    note_particolari = models.TextField(
        blank=True,
        help_text="Ippoterapia, disabilità, allergie, paure, ecc.",
    )

    creato_il = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["cognome", "nome"]
        verbose_name = "allievo"
        verbose_name_plural = "allievi"

    def __str__(self):
        return f"{self.nome} {self.cognome}"

    @property
    def is_minorenne(self):
        oggi = date.today()
        eta = oggi.year - self.data_nascita.year - (
            (oggi.month, oggi.day) < (self.data_nascita.month, self.data_nascita.day)
        )
        return eta < 18


class Documento(models.Model):
    class TipoDocumento(models.TextChoices):
        CERTIFICATO_MEDICO = "certificato_medico", "Certificato medico"
        TESSERA_FISE = "tessera_fise", "Tessera FISE"
        TESSERA_FITETREK = "tessera_fitetrek", "Tessera FITETREK"
        ALTRO = "altro", "Altro"

    allievo = models.ForeignKey(Allievo, on_delete=models.CASCADE, related_name="documenti")
    tipo = models.CharField(max_length=30, choices=TipoDocumento.choices, default=TipoDocumento.ALTRO)
    file = models.FileField(
        upload_to="documenti/%Y/%m/",
        validators=[valida_tipo_documento, valida_dimensione_documento],
        help_text="Solo PDF o immagini (JPG/PNG), max 10 MB.",
    )
    caricato_il = models.DateTimeField(auto_now_add=True)
    note = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ["-caricato_il"]
        verbose_name = "documento"
        verbose_name_plural = "documenti"

    def __str__(self):
        return f"{self.get_tipo_display()} - {self.allievo}"


class ConsensoLog(models.Model):
    """Traccia di un'accettazione consenso dal portale: non è una firma
    digitale qualificata (per quella serve un provider accreditato, es.
    Namirial/InfoCert) ma un'accettazione con timestamp, IP e testo esatto
    mostrato — prova sufficiente di consenso informato per uso interno,
    già più solida del semplice flag booleano che sostituisce.

    Ogni riga è un'accettazione storica: se il testo cambia o il consenso
    va rinnovato, se ne crea una nuova invece di modificare quella
    precedente, così la storia resta consultabile.
    """

    class Tipo(models.TextChoices):
        PRIVACY = "privacy", "Trattamento dati personali"
        FOTO_VIDEO = "foto_video", "Liberatoria foto/video"

    allievo = models.ForeignKey(Allievo, on_delete=models.CASCADE, related_name="consensi")
    tipo = models.CharField(max_length=20, choices=Tipo.choices)
    accettato_il = models.DateTimeField(auto_now_add=True)
    indirizzo_ip = models.GenericIPAddressField(null=True, blank=True)
    testo_accettato = models.TextField(help_text="Copia esatta del testo mostrato al momento dell'accettazione.")

    class Meta:
        ordering = ["-accettato_il"]
        verbose_name = "consenso accettato"
        verbose_name_plural = "consensi accettati"

    def __str__(self):
        return f"{self.get_tipo_display()} - {self.allievo} ({self.accettato_il:%d/%m/%Y %H:%M})"
