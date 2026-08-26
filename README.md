# Gestionale maneggio

Gestionale su misura per la gestione di allievi, cavalli, lezioni, pacchetti e
comunicazioni di un centro ippico. Pensato per essere mantenuto da una sola
persona, non da un team dedicato: stack mainstream, poche parti in
movimento, nessuna pipeline di build separata.

## Stack

- Python 3.10 + Django 5.2
- PostgreSQL
- Bootstrap 5 e FullCalendar auto-ospitati in `static/vendor/` (nessun CDN esterno)
- Nessun framework JS/SPA: solo template Django + un po' di JS per il calendario
  e il formset lezioni

## Setup sviluppo

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # poi compilare almeno DB_NAME/DB_USER/DB_PASSWORD
python manage.py migrate
python manage.py runserver 0.0.0.0:8000
```

Nota per lo sviluppo su questo server: quando si crea la cartella `templates/`
di una app per la prima volta, il processo `runserver` già avviato non se ne
accorge (l'elenco delle directory è messo in cache all'avvio). In quel caso
serve un riavvio pulito del processo, non basta l'autoreload.

## Comandi di gestione

- `python manage.py carica_dati_demo` — popola dati placeholder (allievi,
  cavalli, istruttori, campi, lezioni...). Rilanciabile senza duplicare.
- `python manage.py imposta_ruoli` — crea/aggiorna i gruppi Istruttori/Allievi
  e crea gli account di accesso mancanti (istruttori con accesso admin
  limitato, allievi con accesso al solo portale di sola lettura). Le password
  generate vengono stampate una volta sola, non salvate da nessuna parte:
  vanno comunicate subito e non sono recuperabili in seguito.
- `python manage.py invia_notifiche` — invia i promemoria lezione (il giorno
  prima) e gli alert di scadenza (certificato medico, tessere FISE/FITETREK,
  pacchetto) entro 30 giorni. Pensato per girare una volta al giorno da cron:

  ```cron
  0 8 * * * /percorso/venv/bin/python /percorso/manage.py invia_notifiche >> /percorso/logs/notifiche.log 2>&1
  ```

  È sicuro rilanciarlo più volte: non manda due volte lo stesso avviso (usa
  `comunicazioni.NotificaInviata` come registro di deduplica).

## Email

Di default (`.env` senza `EMAIL_BACKEND`) le email vengono solo stampate sulla
console del server: comodo in sviluppo, non serve un account SMTP per provare
promemoria/alert/broadcast. In produzione, impostare nel `.env`:

```
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=...
EMAIL_HOST_USER=...
EMAIL_HOST_PASSWORD=...
DEFAULT_FROM_EMAIL=...
```

## Ruoli e accesso

- **Admin/segreteria** (superuser): accesso completo, incluso `/admin/`.
- **Istruttori** (gruppo "Istruttori", `is_staff=True`): gestione completa di
  lezioni/partecipazioni, sola lettura su allievi/cavalli/campi/pacchetti,
  nessun accesso ai documenti riservati (certificati, dati sensibili).
- **Allievi/genitori** (gruppo "Allievi", `is_staff=False`): nessun accesso
  admin, solo il portale di sola lettura in `/persone/portale/` (proprie
  lezioni + stato pacchetto). Non possono prenotare o disdire da soli.

## App

| App | Responsabilità |
|---|---|
| `core` | home page, login/logout, cornice del sito |
| `persone` | allievi, tutori, istruttori, proprietari, documenti, portale allievi |
| `cavalli` | anagrafica cavalli (scuola/pensione) |
| `lezioni` | campi, tipi lezione, calendario, form lezione/partecipazioni |
| `pacchetti` | tipi di pacchetto configurabili, pacchetti acquistati |
| `comunicazioni` | promemoria/alert automatici, broadcast (via admin) |
| `report` | presenze/assenze, utilizzo cavalli, occupazione istruttori/campi, scadenze |

## Fuori scope (deciso esplicitamente)

- Pagamenti/fatturazione: nessun incasso tracciato in nessun punto del
  sistema (i pacchetti hanno solo un prezzo di riferimento informativo).
- Prenotazione/disdetta autonoma da parte di allievi: le lezioni le gestiscono
  solo admin/segreteria.
- Lista d'attesa lezioni.
- Regole rigide di preavviso disdetta: a discrezione della segreteria.

## Roadmap MVP

1. ~~Ruoli e permessi~~ ✅
2. ~~Calendario lezioni~~ ✅
3. ~~Portale allievi/genitori~~ ✅
4. ~~Notifiche/comunicazioni~~ ✅
5. ~~Report~~ ✅

Estensioni future possibili (non bloccanti per l'MVP): rifinitura estetica
dedicata, gestione gare/eventi, pagina impostazioni centralizzata, magazzino/
tack room, app mobile, check-in su tablet, fatturazione (fase 2).
