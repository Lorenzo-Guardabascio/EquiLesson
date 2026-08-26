from functools import wraps

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied


def allievo_required(view_func):
    """Consente l'accesso solo ad account collegati a un Allievo (portale di sola lettura)."""

    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        if not hasattr(request.user, "allievo"):
            raise PermissionDenied("Questo account non è collegato a un allievo.")
        return view_func(request, *args, **kwargs)

    return wrapper


def proprietario_required(view_func):
    """Consente l'accesso solo ad account collegati a un Proprietario (portale pensione)."""

    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        if not hasattr(request.user, "proprietario"):
            raise PermissionDenied("Questo account non è collegato a un proprietario.")
        return view_func(request, *args, **kwargs)

    return wrapper
