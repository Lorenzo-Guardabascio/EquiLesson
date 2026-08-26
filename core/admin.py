from django.contrib import admin
from django.shortcuts import redirect
from django.urls import reverse

from .models import Impostazioni


@admin.register(Impostazioni)
class ImpostazioniAdmin(admin.ModelAdmin):
    """Singleton: un solo record, non cancellabile, si va dritti alla scheda di modifica."""

    def has_add_permission(self, request):
        return not Impostazioni.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False

    def changelist_view(self, request, extra_context=None):
        obj = Impostazioni.get()
        return redirect(reverse("admin:core_impostazioni_change", args=[obj.pk]))
