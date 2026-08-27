"""Retema il pannello di Django admin (via django-admin-interface) per farlo
coerente con la nuova estetica del frontend: via il verde acceso a blocchi e
il titolo giallo di default (illeggibile e "cubettoso"), dentro una versione
sobria della stessa palette del brand — intestazione quasi bianca, testo
scuro, verde solo per accenti/pulsanti.

È una migrazione dati (non solo un tocco fatto a mano in produzione) apposta:
ogni nuova installazione del gestionale deve partire già con questo aspetto
via `manage.py migrate`, senza bisogno di rimettere mano al tema ogni volta.
"""
from django.db import migrations


def imposta_tema(apps, schema_editor):
    Theme = apps.get_model("admin_interface", "Theme")
    Theme.objects.update_or_create(
        name="Django",
        defaults=dict(
            active=True,
            title="EquiLesson",
            title_color="#1c1f1b",
            title_visible=True,
            css_header_background_color="#ffffff",
            css_header_text_color="#1f5c33",
            css_header_link_color="#1c1f1b",
            css_header_link_hover_color="#2e7d46",
            css_module_background_color="#eaf5ee",
            css_module_background_selected_color="#d5e9da",
            css_module_text_color="#1c1f1b",
            css_module_link_color="#1c1f1b",
            css_module_link_selected_color="#1f5c33",
            css_module_link_hover_color="#2e7d46",
            css_module_rounded_corners=True,
            css_generic_link_color="#2e7d46",
            css_generic_link_hover_color="#1f5c33",
            css_generic_link_active_color="#1f5c33",
            css_save_button_background_color="#2e7d46",
            css_save_button_background_hover_color="#1f5c33",
            css_save_button_text_color="#ffffff",
            css_delete_button_background_color="#a1352b",
            css_delete_button_background_hover_color="#7e2a22",
            css_delete_button_text_color="#ffffff",
        ),
    )


def ripristina_tema_default(apps, schema_editor):
    Theme = apps.get_model("admin_interface", "Theme")
    Theme.objects.filter(name="Django").update(
        title="Amministrazione di Django",
        title_color="#F5DD5D",
        css_header_background_color="#0C4B33",
        css_header_text_color="#44B78B",
        css_header_link_color="#FFFFFF",
        css_header_link_hover_color="#C9F0DD",
        css_module_background_color="#44B78B",
        css_module_background_selected_color="#FFFFCC",
        css_module_text_color="#FFFFFF",
        css_module_link_color="#FFFFFF",
        css_module_link_selected_color="#FFFFFF",
        css_module_link_hover_color="#C9F0DD",
        css_generic_link_color="#0C3C26",
        css_generic_link_hover_color="#156641",
        css_generic_link_active_color="#29B864",
        css_save_button_background_color="#0C4B33",
        css_save_button_background_hover_color="#0C3C26",
        css_delete_button_background_color="#BA2121",
        css_delete_button_background_hover_color="#A41515",
    )


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0001_initial"),
        ("admin_interface", "0032_alter_theme_defaults"),
    ]

    operations = [
        migrations.RunPython(imposta_tema, ripristina_tema_default),
    ]
