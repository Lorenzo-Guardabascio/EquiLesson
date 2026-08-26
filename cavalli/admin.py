from django.contrib import admin

from .models import Cavallo


@admin.register(Cavallo)
class CavalloAdmin(admin.ModelAdmin):
    list_display = ("nome", "tipo", "livello_impiego", "disponibile", "proprietario")
    list_filter = ("tipo", "livello_impiego", "disponibile")
    search_fields = ("nome", "microchip")
