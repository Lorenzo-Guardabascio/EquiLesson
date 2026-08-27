def menu_gestione(request):
    """Espone le voci di 'Gestione' visibili all'utente corrente su OGNI
    pagina (non solo su quelle di gestione): serve alla navbar in
    core/base.html, che deve poter mostrare il menu ovunque, non solo
    quando ci si trova già dentro una delle sue pagine."""
    user = getattr(request, "user", None)
    if user is None or not user.is_authenticated or not user.is_staff:
        return {}
    from .gestione_config import voci_per_nav
    return {"gruppi_gestione_nav": voci_per_nav(user)}
