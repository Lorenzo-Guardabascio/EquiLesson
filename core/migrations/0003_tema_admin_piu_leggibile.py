"""Corregge una regressione di leggibilità introdotta dalla 0002: le barre
di sezione dell'admin (intestazioni "Autenticazione e autorizzazione",
"Cavalli", ecc., più le breadcrumb) usavano testo quasi nero su un verde
menta molto chiaro (#eaf5ee) — tecnicamente sopra la soglia minima di
contrasto, ma percettivamente "lavato via": tutte le sezioni si confondono
nella stessa tinta pallida, difficile da scandire a colpo d'occhio.

Si torna al pattern classico (anche di Django stesso): barra a tinta piena
col colore del brand, testo bianco sopra. Massimo contrasto possibile,
comunque riconoscibile come "nostro" grazie al verde invece del
blu/grigio di default — niente a che vedere con l'effetto "a cubetti"
delle pillole/riempimenti pieni sui CONTROLLI di modulo (quello era il
problema della 0002 lato frontend, qui stiamo sistemando solo le barre
di intestazione dell'admin tecnico)."""
from django.db import migrations


def imposta_tema(apps, schema_editor):
    Theme = apps.get_model("admin_interface", "Theme")
    Theme.objects.filter(name="Django").update(
        css_module_background_color="#2e7d46",
        css_module_text_color="#ffffff",
        css_module_link_color="#ffffff",
        css_module_link_selected_color="#ffffff",
        css_module_link_hover_color="#eaf5ee",
    )


def ripristina_tema_precedente(apps, schema_editor):
    Theme = apps.get_model("admin_interface", "Theme")
    Theme.objects.filter(name="Django").update(
        css_module_background_color="#eaf5ee",
        css_module_text_color="#1c1f1b",
        css_module_link_color="#1c1f1b",
        css_module_link_selected_color="#1f5c33",
        css_module_link_hover_color="#2e7d46",
    )


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0002_tema_admin_equilesson"),
    ]

    operations = [
        migrations.RunPython(imposta_tema, ripristina_tema_precedente),
    ]
