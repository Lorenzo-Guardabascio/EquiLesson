from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'

    def ready(self):
        _restringi_admin_al_sistemista()


def _restringi_admin_al_sistemista():
    """L'admin di Django (/admin/) è pensato come pannello tecnico per chi
    gestisce l'installazione (il "sistemista"), non per l'uso quotidiano di
    segreteria/istruttori — quello passa dal frontend (vedi core.gestione).
    Di default basterebbe is_staff per entrare in admin: qui si restringe
    esplicitamente ai soli superuser, così il confine resta netto anche se
    in futuro qualcuno desse per errore is_staff=True a un account che non
    dovrebbe avere accesso al pannello tecnico."""
    from django.contrib import admin

    admin.site.has_permission = lambda request: (
        request.user.is_active and request.user.is_superuser
    )
