from functools import wraps

from django.contrib import messages
from django.shortcuts import redirect


def richiede_impostazione(check, redirect_to, messaggio):
    """Blocca una vista se `check()` restituisce False.

    Usato per le funzionalità attivabili/disattivabili da `core.Impostazioni`
    (es. prenotazione autonoma allievi): se l'admin la disattiva, chi prova ad
    accedere alla vista viene rimandato indietro con un messaggio invece di
    vedere un errore.
    """

    def decoratore(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not check():
                messages.info(request, messaggio)
                return redirect(redirect_to)
            return view_func(request, *args, **kwargs)

        return wrapper

    return decoratore
