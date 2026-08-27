"""Genera locale/en/LC_MESSAGES/django.po + .mo a mano, con polib.

Serve perché xgettext/msgfmt (gettext-tools) potrebbero non essere installati
(non lo erano sul server originale, senza sudo per aggiungerli):
`manage.py makemessages`/`compilemessages` standard richiedono quei
programmi e falliscono senza. Se sul tuo sistema xgettext/msgfmt SONO
disponibili, usa pure i comandi standard di Django invece di questo script.

I msgid qui sotto sono stati raccolti a mano grep-ando ogni
{% trans %}/{% blocktrans %} nei template e ogni gettext()/gettext_lazy()
nelle view — se aggiungi nuove stringhe traducibili, aggiungile anche qui e
rilancia questo script (richiede `pip install polib`).

Uso:
    python locale/genera_traduzioni.py
"""
import pathlib

import polib

TRADUZIONI = {
    # --- stringhe semplici (trans) ---
    "Accedi": "Log in",
    "Accedi per continuare.": "Log in to continue.",
    "Accettato": "Accepted",
    "Accetto": "Accept",
    "Aggiungi partecipante": "Add participant",
    "Al": "To",
    "Allievi attivi": "Active students",
    "Allievi in scadenza (prossimi 30 giorni)": "Students with upcoming expiries (next 30 days)",
    "Allievo": "Student",
    "Amministrazione": "Administration",
    "Annulla": "Cancel",
    "Annullata": "Cancelled",
    "Applica": "Apply",
    "Apri": "Open",
    "Assenti": "Absent",
    "Box": "Stall",
    "Calendario": "Calendar",
    "Calendario lezioni": "Lesson calendar",
    "Campo": "Arena",
    "Cavalli": "Horses",
    "Cavalli: scadenze sanitarie (prossimi 30 giorni)": "Horses: health due dates (next 30 days)",
    "Cavallo": "Horse",
    "Certificati medici in scadenza (30 giorni)": "Medical certificates expiring (30 days)",
    "Codice non valido.": "Invalid code.",
    "Confermata": "Confirmed",
    "Consensi": "Consents",
    "Consulta le tue prossime lezioni e il pacchetto residuo.": "Check your upcoming lessons and remaining package.",
    "Consulta lo stato del tuo cavallo e le prossime scadenze sanitarie.": "Check your horse's status and upcoming health due dates.",
    "Dal": "From",
    "Data": "Date",
    "Dati della lezione": "Lesson details",
    "e invia questo messaggio:": "and send this message:",
    "Elimina lezione": "Delete lesson",
    "Eliminare questa lezione?": "Delete this lesson?",
    "Esci": "Log out",
    "Esporta CSV": "Export CSV",
    "Esporta PDF": "Export PDF",
    "Genera codice di collegamento": "Generate linking code",
    "Gestionale maneggio": "EquiLesson",
    "Home": "Home",
    "il bot Telegram del centro": "the center's Telegram bot",
    "Il collegamento avviene entro qualche minuto dall'invio.": "The link is completed within a few minutes of sending.",
    "Il mio cavallo": "My horse",
    "Il mio pacchetto": "My package",
    "Il mio portale": "My portal",
    "Il periodo si applica a presenze, utilizzo cavalli e occupazione istruttori/campi.": "The period applies to attendance, horse usage, and instructor/arena occupancy.",
    "In scadenza": "Expiring",
    "Istruttore": "Instructor",
    "L'accettazione viene registrata con data/ora e indirizzo IP, insieme al testo esatto mostrato qui sopra.": "Acceptance is recorded with date/time and IP address, along with the exact text shown above.",
    "La mia tessera": "My membership card",
    "Lezioni svolte oltre a quelle incluse nel pacchetto.": "Lessons taken beyond what's included in the package.",
    "Le mie lezioni": "My lessons",
    "Lezioni": "Lessons",
    "Lezioni oggi": "Lessons today",
    "Lezioni passate (ultime 10)": "Past lessons (last 10)",
    "Nessuna lezione aperta alla prenotazione al momento.": "No lessons currently open for booking.",
    "Nessuna lezione in programma.": "No lessons scheduled.",
    "Nessuna lezione nel periodo.": "No lessons in this period.",
    "Nessuna lezione passata registrata.": "No past lessons recorded.",
    "Nessuna partecipazione nel periodo.": "No participation in this period.",
    "Nessuna scadenza imminente.": "No upcoming expiries.",
    "Nessuna scadenza nei prossimi 30 giorni.": "No expiries in the next 30 days.",
    "Nessuna scadenza registrata.": "No due dates recorded.",
    "Nessuna scadenza sanitaria nei prossimi 30 giorni.": "No health due dates in the next 30 days.",
    "Nessun pacchetto attivo al momento.": "No active package at the moment.",
    "Nessun pacchetto registrato.": "No packages recorded.",
    "Nessun utilizzo nel periodo.": "No usage in this period.",
    "Nome utente": "Username",
    "Nome utente o password non corretti.": "Incorrect username or password.",
    "Non ancora accettato": "Not yet accepted",
    "Non risulta nessun cavallo in pensione a tuo nome.": "No boarding horse is registered under your name.",
    "Note": "Notes",
    "Notifiche su Telegram": "Telegram notifications",
    "Nuova lezione": "New lesson",
    "Occupazione campi": "Arena occupancy",
    "Occupazione istruttori": "Instructor occupancy",
    "Ora fine": "End time",
    "Ora inizio": "Start time",
    "Pacchetto": "Package",
    "Partecipanti": "Participants",
    "Password": "Password",
    "Per motivi di riservatezza questa pagina non mostra certificato medico o note: per quei dati consulta la scheda completa in amministrazione.": "For privacy reasons this page doesn't show the medical certificate or notes: for that data check the full record in administration.",
    "portale": "portal",
    "Prenota": "Book",
    "Prenotata": "Booked",
    "Prenota una lezione": "Book a lesson",
    "Presenze/assenze per allievo": "Attendance/absences per student",
    "Prossime lezioni": "Upcoming lessons",
    "Prossime scadenze sanitarie": "Upcoming health due dates",
    "Razza": "Breed",
    "Report": "Reports",
    "Ricevi i promemoria delle lezioni e gli alert di scadenza anche su Telegram.": "Get lesson reminders and expiry alerts on Telegram too.",
    "Rimuovi": "Remove",
    "Salva lezione": "Save lesson",
    "Scadenza": "Due date",
    "Scaduto": "Expired",
    "Scollega": "Unlink",
    "seleziona": "select",
    "Sì, elimina": "Yes, delete",
    "Stato": "Status",
    "Storico pacchetti": "Package history",
    "Svolta": "Completed",
    "Svolte": "Completed",
    "Telegram collegato: riceverai qui promemoria e avvisi.": "Telegram linked: you'll receive reminders and alerts here.",
    "Tessera FISE": "FISE membership card",
    "Tessera FITETREK": "FITETREK membership card",
    "Tipo": "Type",
    "Tipo di lezione": "Lesson type",
    "Torna al calendario": "Back to calendar",
    "Torna al portale": "Back to portal",
    "Un istruttore o la segreteria può inquadrare questo codice per verificare rapidamente il tuo tesseramento.": "An instructor or the front desk can scan this code to quickly verify your membership.",
    "Utilizzo cavalli": "Horse usage",
    "Vai all'amministrazione": "Go to administration",
    "Vai al mio portale": "Go to my portal",
    "Verifica tessera": "Verify membership card",
    "Lingua": "Language",
    "QR della tessera": "Membership card QR code",

    # --- menu "Gestione" e viste generiche (core/gestione*.py) ---
    "Gestione": "Manage",
    "Amministrazione tecnica": "Technical admin",
    "Nuovo": "New",
    "Modifica": "Edit",
    "Elimina": "Delete",
    "Cerca…": "Search…",
    "Nessun risultato.": "No results.",
    "Salva": "Save",
    'Eliminare "%(elemento)s"?': 'Delete "%(elemento)s"?',
    "%(voce)s salvato correttamente.": "%(voce)s saved successfully.",
    "%(voce)s eliminato.": "%(voce)s deleted.",

    # --- voci di gestione: etichette di menu, colonne, campi ---
    "Allievi": "Students",
    "allievo": "student",
    "Persone": "People",
    "Nome": "First name",
    "Cognome": "Last name",
    "Telefono": "Phone",
    "Scadenza certificato": "Certificate due date",
    "Tutori": "Guardians",
    "tutore": "guardian",
    "Istruttori": "Instructors",
    "istruttore": "instructor",
    "Attivo": "Active",
    "Proprietari": "Owners",
    "proprietario": "owner",
    "cavallo": "horse",
    "Livello": "Level",
    "Disponibile": "Available",
    "Pacchetti": "Packages",
    "pacchetto": "package",
    "Residue": "Remaining",
    "Tipi di pacchetto": "Package types",
    "tipo di pacchetto": "package type",
    "N. lezioni": "No. of lessons",
    "Campi": "Arenas",
    "campo": "arena",
    "Tipi di lezione": "Lesson types",
    "tipo di lezione": "lesson type",
    "Durata (min)": "Duration (min)",
    "Sì": "Yes",
    "No": "No",

    # --- blocktrans (con placeholder %(nome)s, esattamente come li estrae Django) ---
    "Il cavallo ti verrà assegnato dalla segreteria dopo la prenotazione. Puoi annullare in qualsiasi momento dal tuo":
        "The horse will be assigned by the front desk after booking. You can cancel at any time from your",
    "%(n)s/%(max)s posti": "%(n)s/%(max)s spots",
    "Bentornato, %(name)s": "Welcome back, %(name)s",
    "Ciao, %(name)s": "Hi, %(name)s",
    "Ciao, %(nome)s": "Hi, %(nome)s",
    "scade il %(data)s": "expires on %(data)s",
    "%(tot)s lezioni residue": "%(tot)s lessons remaining",
    "Valido fino al %(data)s": "Valid until %(data)s",
    "dal %(dal)s al %(al)s": "from %(dal)s to %(al)s",
    "%(res)s/%(tot)s residue": "%(res)s/%(tot)s remaining",
    "il %(data)s": "on %(data)s",
    "scad. %(data)s": "exp. %(data)s",

    # --- messaggi lato view (gettext) ---
    "Codice generato: invialo al bot Telegram come indicato qui sotto.": "Code generated: send it to the Telegram bot as shown below.",
    "Consenso registrato.": "Consent recorded.",
    "Lezione eliminata.": "Lesson deleted.",
    "Lezione salvata correttamente.": "Lesson saved successfully.",
    "Non puoi annullare una lezione già passata.": "You can't cancel a lesson that has already passed.",
    "Prenotazione annullata.": "Booking cancelled.",
    "Prenotazione registrata: il cavallo ti verrà assegnato dalla segreteria.": "Booking recorded: the horse will be assigned by the front desk.",
    "Questa lezione è nel frattempo diventata al completo.": "This lesson has since become full.",
    "Questa lezione non è più prenotabile.": "This lesson can no longer be booked.",
    "Sei già iscritto a questa lezione.": "You're already registered for this lesson.",
    "Telegram scollegato.": "Telegram unlinked.",
    "La prenotazione autonoma non è attiva al momento: contatta la segreteria.":
        "Self-booking isn't active at the moment: contact the front desk.",
}


def main():
    po = polib.POFile()
    po.metadata = {
        "Project-Id-Version": "EquiLesson",
        "Report-Msgid-Bugs-To": "",
        "MIME-Version": "1.0",
        "Content-Type": "text/plain; charset=UTF-8",
        "Content-Transfer-Encoding": "8bit",
        "Language": "en",
    }
    for msgid, msgstr in TRADUZIONI.items():
        po.append(polib.POEntry(msgid=msgid, msgstr=msgstr))

    out_dir = pathlib.Path(__file__).resolve().parent / "en" / "LC_MESSAGES"
    out_dir.mkdir(parents=True, exist_ok=True)
    po.save(str(out_dir / "django.po"))
    po.save_as_mofile(str(out_dir / "django.mo"))
    print(f"Scritte {len(TRADUZIONI)} voci in {out_dir}")


if __name__ == "__main__":
    main()
