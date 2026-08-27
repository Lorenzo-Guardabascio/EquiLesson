"""Validazione dei documenti caricati (certificati medici, tessere...).

Prima non c'era alcun controllo: si poteva caricare qualsiasi file, di
qualsiasi dimensione — un rischio concreto dato che questi allegati
contengono dati sanitari e di minorenni. Il controllo sul contenuto reale
(magic bytes via `filetype`, non solo l'estensione del nome file, che chiunque
può falsificare) evita che un file rinominato ad arte passi come PDF/immagine.
"""

import os

import filetype
from django.core.exceptions import ValidationError

DIMENSIONE_MASSIMA_MB = 10
ESTENSIONI_CONSENTITE = {".pdf", ".jpg", ".jpeg", ".png"}
MIME_CONSENTITI = {"application/pdf", "image/jpeg", "image/png"}


def valida_tipo_documento(value):
    estensione = os.path.splitext(value.name)[1].lower()
    if estensione not in ESTENSIONI_CONSENTITE:
        raise ValidationError(
            "Tipo di file non consentito: sono ammessi solo PDF e immagini (JPG, PNG)."
        )

    intestazione = value.read(2048)
    value.seek(0)
    tipo_rilevato = filetype.guess(intestazione)
    if tipo_rilevato is None or tipo_rilevato.mime not in MIME_CONSENTITI:
        raise ValidationError(
            "Il contenuto del file non corrisponde a un PDF o un'immagine valida "
            "(un file rinominato con l'estensione sbagliata non basta a superare il controllo)."
        )


def valida_dimensione_documento(value):
    limite_byte = DIMENSIONE_MASSIMA_MB * 1024 * 1024
    if value.size > limite_byte:
        raise ValidationError(f"File troppo grande: il limite è {DIMENSIONE_MASSIMA_MB} MB.")
