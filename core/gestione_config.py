"""Registro delle voci di "Gestione" (anagrafica/configurazione) esposte nel
frontend invece che solo nell'admin di Django.

Fino ad oggi Allievi, Cavalli, Pacchetti, Tutori, Istruttori, Proprietari,
Documenti, Campi, Tipi di lezione/pacchetto, Comunicazioni ecc. si gestivano
SOLO da /admin/ — da qui la sensazione di "due siti separati" (nav custom da
una parte, pannello Django dall'altra). L'admin resta, ma solo come pannello
tecnico per il sistemista (vedi core/apps.py, accesso ristretto ai
superuser): la segreteria deve poter fare tutto dal frontend.

Un registro unico invece di 9 viste/template quasi identici scritti a mano:
ogni voce descrive un modello con pochi dati dichiarativi (campi da mostrare
in lista, campi del form, permesso richiesto) e core.gestione fornisce le
viste generiche lista/form/elimina che li interpretano. Non è un ORM-scaffold
alla Django-admin: i template sono i nostri, temati come il resto del sito,
e il pacchetto di permessi è lo stesso già usato altrove (Django auth), così
lo stesso gruppo "Istruttori" creato da `imposta_ruoli` vale identico se
usato da qui o dall'admin.
"""
from dataclasses import dataclass, field

from django.utils.translation import gettext_lazy as _


@dataclass
class Inline:
    """Un formset inline mostrato dentro il form della voce principale
    (es. i Documenti dentro il form di un Allievo)."""

    model: type
    fk_name: str
    campi: list
    etichetta: str
    extra: int = 2


@dataclass
class Voce:
    slug: str
    model: type
    etichetta: str          # es. "Allievi" — titolo lista, voce di menu
    etichetta_singolare: str  # es. "allievo" — usato nei messaggi
    campi_form: list
    colonne: list            # [(etichetta, percorso_valore), ...] per la tabella
    cerca_campi: tuple = ()
    inline: Inline | None = None
    sola_lettura: bool = False   # log di sistema: solo consultazione, mai add/change/delete
    gruppo_nav: str = ""         # raggruppamento nel menu "Gestione"

    @property
    def app_label(self):
        return self.model._meta.app_label

    @property
    def model_name(self):
        return self.model._meta.model_name

    def permesso(self, azione):
        return f"{self.app_label}.{azione}_{self.model_name}"


def _registro():
    # Import qui dentro (non in cima al modulo) per evitare dipendenze da
    # ordine di caricamento delle app: questo modulo viene importato da
    # core.urls, quindi ben dopo che tutte le app sono pronte, ma tenerlo
    # comunque pigro costa nulla ed evita sorprese future.
    from cavalli.models import Cavallo, ScadenzaSanitaria
    from lezioni.models import Campo, TipoLezione
    from pacchetti.models import Pacchetto, TipoPacchetto
    from persone.models import Allievo, Documento, Istruttore, Proprietario, Tutore

    voci = [
        Voce(
            slug="allievi",
            model=Allievo,
            etichetta=_("Allievi"),
            etichetta_singolare=_("allievo"),
            gruppo_nav=_("Persone"),
            campi_form=[
                "nome", "cognome", "data_nascita", "codice_fiscale", "telefono", "email",
                "indirizzo", "tutori", "stato",
                "certificato_medico_tipo", "certificato_medico_scadenza",
                "tessera_fise_numero", "tessera_fise_scadenza",
                "tessera_fitetrek_numero", "tessera_fitetrek_scadenza",
                "consenso_privacy", "consenso_foto_video",
                "propensione", "note_particolari",
            ],
            colonne=[(_("Cognome"), "cognome"), (_("Nome"), "nome"), (_("Stato"), "get_stato_display"),
                     (_("Scadenza certificato"), "certificato_medico_scadenza")],
            cerca_campi=("nome", "cognome", "codice_fiscale"),
            inline=Inline(
                model=Documento, fk_name="allievo",
                campi=["tipo", "file", "note"], etichetta=_("Documenti"),
            ),
        ),
        Voce(
            slug="tutori",
            model=Tutore,
            etichetta=_("Tutori"),
            etichetta_singolare=_("tutore"),
            gruppo_nav=_("Persone"),
            campi_form=["nome", "cognome", "relazione", "telefono", "email"],
            colonne=[(_("Cognome"), "cognome"), (_("Nome"), "nome"), (_("Telefono"), "telefono")],
            cerca_campi=("nome", "cognome"),
        ),
        Voce(
            slug="istruttori",
            model=Istruttore,
            etichetta=_("Istruttori"),
            etichetta_singolare=_("istruttore"),
            gruppo_nav=_("Persone"),
            campi_form=["nome", "cognome", "telefono", "email", "note_disponibilita", "attivo"],
            colonne=[(_("Cognome"), "cognome"), (_("Nome"), "nome"), (_("Attivo"), "attivo")],
            cerca_campi=("nome", "cognome"),
        ),
        Voce(
            slug="proprietari",
            model=Proprietario,
            etichetta=_("Proprietari"),
            etichetta_singolare=_("proprietario"),
            gruppo_nav=_("Persone"),
            campi_form=["nome", "cognome", "telefono", "email"],
            colonne=[(_("Cognome"), "cognome"), (_("Nome"), "nome"), (_("Telefono"), "telefono")],
            cerca_campi=("nome", "cognome"),
        ),
        Voce(
            slug="cavalli",
            model=Cavallo,
            etichetta=_("Cavalli"),
            etichetta_singolare=_("cavallo"),
            gruppo_nav=_("Cavalli"),
            campi_form=[
                "nome", "razza", "data_nascita", "sesso", "microchip", "tipo", "proprietario",
                "livello_impiego", "disponibile", "note_disponibilita", "box", "note_sanitarie",
            ],
            colonne=[(_("Nome"), "nome"), (_("Tipo"), "get_tipo_display"),
                     (_("Livello"), "get_livello_impiego_display"), (_("Disponibile"), "disponibile")],
            cerca_campi=("nome", "razza", "microchip"),
            inline=Inline(
                model=ScadenzaSanitaria, fk_name="cavallo",
                campi=["tipo", "data_scadenza", "note"], etichetta=_("Scadenze sanitarie"),
            ),
        ),
        Voce(
            slug="pacchetti",
            model=Pacchetto,
            etichetta=_("Pacchetti"),
            etichetta_singolare=_("pacchetto"),
            gruppo_nav=_("Pacchetti"),
            campi_form=["allievo", "tipo_pacchetto", "data_inizio", "data_scadenza", "lezioni_totali", "stato", "note"],
            colonne=[(_("Allievo"), "allievo"), (_("Tipo"), "tipo_pacchetto"),
                     (_("Residue"), "lezioni_residue"), (_("Stato"), "get_stato_display")],
            cerca_campi=("allievo__nome", "allievo__cognome"),
        ),
        Voce(
            slug="tipi-pacchetto",
            model=TipoPacchetto,
            etichetta=_("Tipi di pacchetto"),
            etichetta_singolare=_("tipo di pacchetto"),
            gruppo_nav=_("Pacchetti"),
            campi_form=["nome", "numero_lezioni", "durata_giorni", "prezzo", "prezzo_scontato_pensione", "attivo"],
            colonne=[(_("Nome"), "nome"), (_("N. lezioni"), "numero_lezioni"), (_("Attivo"), "attivo")],
            cerca_campi=("nome",),
        ),
        Voce(
            slug="campi",
            model=Campo,
            etichetta=_("Campi"),
            etichetta_singolare=_("campo"),
            gruppo_nav=_("Lezioni"),
            campi_form=["nome", "note"],
            colonne=[(_("Nome"), "nome"), (_("Note"), "note")],
            cerca_campi=("nome",),
        ),
        Voce(
            slug="tipi-lezione",
            model=TipoLezione,
            etichetta=_("Tipi di lezione"),
            etichetta_singolare=_("tipo di lezione"),
            gruppo_nav=_("Lezioni"),
            campi_form=["nome", "durata_default_minuti", "capienza_max", "attivo"],
            colonne=[(_("Nome"), "nome"), (_("Durata (min)"), "durata_default_minuti"), (_("Attivo"), "attivo")],
            cerca_campi=("nome",),
        ),
    ]
    return {v.slug: v for v in voci}


REGISTRO = _registro()


def voci_per_nav(user):
    """Raggruppa le voci visibili per l'utente (permesso view_* sul modello),
    mantenendo l'ordine di inserimento, per popolare il menu "Gestione"."""
    gruppi = {}
    for voce in REGISTRO.values():
        if not user.has_perm(voce.permesso("view")):
            continue
        gruppi.setdefault(voce.gruppo_nav, []).append(voce)
    return gruppi
