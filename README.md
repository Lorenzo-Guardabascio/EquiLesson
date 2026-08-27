**English** (below) · [**Italiano** ↓](#equilesson-italiano)

# EquiLesson

Open source management software for equestrian centers: students, horses,
lessons, lesson packages and communications. Started as an internal project
for a real riding school, built to be maintained by one person rather than
a dedicated team: mainstream stack, few moving parts, no separate build
pipeline.

## Stack

- Python 3.10 + Django 5.2
- PostgreSQL
- Bootstrap 5 and FullCalendar, self-hosted under `static/vendor/` (no external CDN)
- No JS/SPA framework: Django templates plus a bit of JS for the calendar
  and the lesson formset

## Development setup

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # then fill in at least DB_NAME/DB_USER/DB_PASSWORD
python manage.py migrate
python manage.py runserver 0.0.0.0:8000
```

Development note: when a `templates/` folder is created for an app for the
first time, an already-running `runserver` process won't notice (the list of
template directories is cached at startup). In that case you need a clean
restart of the process — plain autoreload isn't enough.

## Management commands

- `python manage.py carica_dati_demo` — loads placeholder data (students,
  horses, instructors, arenas, lessons...). Safe to run again without
  duplicating data.
- `python manage.py imposta_ruoli` — creates/updates the Instructors/Students
  groups and creates missing login accounts (instructors get limited admin
  access, students get access to the read-only portal only). Generated
  passwords are printed once and never saved anywhere: pass them on right
  away, they can't be recovered later.
- `python manage.py invia_notifiche` — sends lesson reminders (the day
  before) and expiry alerts (medical certificate, federation membership
  cards, lesson package) within 30 days. Meant to run once a day via cron:

  ```cron
  0 8 * * * /path/venv/bin/python /path/manage.py invia_notifiche >> /path/logs/notifiche.log 2>&1
  ```

  Safe to run more than once: it won't send the same alert twice (uses
  `comunicazioni.NotificaInviata` as a deduplication log).
- `python manage.py telegram_poll` — reads incoming Telegram messages and
  links student accounts that send `/link <code>` from the portal. Meant to
  run every 1-2 minutes via cron; a no-op if `TELEGRAM_BOT_TOKEN` isn't set.

## Email

By default (`.env` with no `EMAIL_BACKEND`) emails are only printed to the
server console: convenient in development, no SMTP account needed to try out
reminders/alerts/broadcasts. In production, set in `.env`:

```
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=...
EMAIL_HOST_USER=...
EMAIL_HOST_PASSWORD=...
DEFAULT_FROM_EMAIL=...
```

## Telegram and WhatsApp notifications

Both are optional, additive channels on top of email, each with its own
on/off switch in `/admin/core/impostazioni/` (both off by default):

- **Telegram** is fully implemented: create a bot with
  [@BotFather](https://t.me/BotFather), put the token in `TELEGRAM_BOT_TOKEN`
  in `.env`, enable it in Impostazioni, and schedule `telegram_poll` in cron.
  Students link their account themselves from the portal (no webhook needed
  — the server doesn't need a public IP, it polls Telegram instead).
- **WhatsApp** is scaffolded against the Meta WhatsApp Business Cloud API
  (`WHATSAPP_ACCESS_TOKEN` / `WHATSAPP_PHONE_NUMBER_ID` in `.env`) but has
  never been exercised against a real account — it requires your own
  verified Meta Business setup, which this project can't provide. Review
  `comunicazioni/canali/whatsapp.py` before relying on it.

## Roles and access

- **Admin/front desk** (superuser): full access, including `/admin/`.
- **Instructors** ("Instructors" group, `is_staff=True`): full management of
  lessons/participations, read-only on students/horses/arenas/packages, no
  access to restricted documents (certificates, sensitive data).
- **Students/parents** ("Students" group, `is_staff=False`): no admin
  access, a portal at `/persone/portale/` with their own lessons and
  package status. If the administrator turns on "Self-booking" (in
  `/admin/core/impostazioni/`, **off by default**), they can also
  book/cancel their own participation in lessons with open spots — the
  horse is still assigned by the front desk.

## Apps

| App | Responsibility |
|---|---|
| `core` | home page, login/logout, site frame, global settings |
| `persone` | students, guardians, instructors, horse owners, documents, student portal |
| `cavalli` | horse records (school horses / boarders) |
| `lezioni` | arenas, lesson types, calendar, lesson/participation form, self-booking |
| `pacchetti` | configurable package types, purchased packages |
| `comunicazioni` | reminders/alerts (email, Telegram, WhatsApp), broadcasts |
| `report` | attendance, horse usage, instructor/arena occupancy, expiries |

## Language switcher (Italian/English)

The app has a language switcher in the navbar (Italian and English), backed
by Django's standard session-based i18n — no URL prefixes, so existing links
(including the ones embedded in the QR membership cards) keep working
regardless of language. Coverage: navigation, buttons, headings, and view
messages across the main templates. **Not yet translated**: Django admin
field labels and model choices (e.g. lesson/package type names) — the admin
is expected to stay Italian-only for now, since day-to-day staff use is in
Italian; this is a known gap, not an oversight.

Translations live in `locale/en/LC_MESSAGES/django.po` (+ compiled
`django.mo`). Normally you'd regenerate these with Django's
`makemessages`/`compilemessages`, but those require the `gettext` system
package (`xgettext`/`msgfmt`), which may not be available everywhere without
root. If you don't have it either, `locale/genera_traduzioni.py` builds the
`.po`/`.mo` files directly with `polib` (pure Python, no system package) from
a hand-maintained dictionary of strings — update that dictionary and rerun
the script when you add new translatable text. If `gettext` **is** available
on your system, just use the standard Django commands instead.

## Out of scope (deliberately)

- Payments/invoicing: no revenue is tracked anywhere in the system
  (packages only carry an informational reference price).
- Automatic lesson waitlist: at the scale of a typical riding school it's
  handled faster by a phone call than it would be worth building and
  maintaining.
- Tracking a student's technical level/progression: EquiLesson only records
  what a student is aiming for (jumping, dressage, trail riding...), not a
  skill assessment.
- Rigid cancellation-notice rules: left to the front desk's judgement, the
  system doesn't enforce them.
- A centralized multi-tenant platform: every installation is independent
  (see "Adopting it for your own riding school").

## Roadmap

**MVP (complete):**

1. ~~Roles and permissions~~ ✅
2. ~~Lesson calendar~~ ✅
3. ~~Student/parent portal~~ ✅
4. ~~Notifications/communications~~ ✅
5. ~~Reports~~ ✅

**Phase 2 (in progress), prompted by a look at other software in the field:**

- [x] Self-booking for students, toggleable by the admin
- [x] Telegram notifications (WhatsApp scaffolded, unverified)
- [ ] Structured health-due-dates for horses (vaccinations, farrier visits,
      deworming) with automatic reminders
- [ ] CSV/PDF export for reports
- [ ] Read-only portal for boarding-horse owners
- [ ] Privacy/liability consent with tracked acceptance (a timestamp, not
      just a checkbox)
- [ ] Digital membership card with QR code for students
- [x] Bilingual Italian/English interface (templates and view messages; admin labels still Italian-only)

Possible future extensions (not blocking): a dedicated visual design pass,
competitions/events management, horse feeding plans, tack room inventory,
a mobile app, tablet check-in, invoicing, a public website for the center.

## Adopting it for your own riding school

The distribution model is **one independent installation per center** (no
multi-tenancy, no data from multiple riding schools in the same database):
every facility gets its own copy, configurable in its lesson types, package
sizes, arenas, and so on. You can clone the repo and install it yourself
following "Development setup" above (production additionally needs a
dedicated Postgres database and a reverse proxy with HTTPS in front of
Django — not yet documented in detail in this repo).

**Like the project?** The code stays free under AGPL-3.0: you can download
it and run it yourself without owing me anything. If you'd rather not deal
with it yourself — installation on your own server, customization for your
center, migrating existing data, ongoing support — that's a paid service:
open an issue or write to dragonknigth09@gmail.com. The project stays free,
my time doesn't.

## License

Distributed under [GNU AGPL-3.0](LICENSE). In short: you may use, modify and
redistribute the code freely, including for commercial purposes, but if you
use it to run a service reachable over a network (even just for a single
riding school, not necessarily for sale) you must make the complete source
code — including your modifications — available to whoever uses that
service. No such condition applies to purely internal use that isn't
exposed to others over a network.

## Security

The system handles sensitive data (medical certificates, data belonging to
minors). To responsibly report a vulnerability, see [SECURITY.md](SECURITY.md).

## Contributing

Contributions, bug reports and proposals are welcome: see
[CONTRIBUTING.md](CONTRIBUTING.md).

---

[**English** ↑](#equilesson) · **Italiano** (sotto)

# EquiLesson (Italiano)

Gestionale open source per centri ippici: allievi, cavalli, lezioni,
pacchetti e comunicazioni. Nasce come progetto interno per un maneggio reale,
pensato per essere mantenuto da una sola persona anziché da un team dedicato:
stack mainstream, poche parti in movimento, nessuna pipeline di build
separata.

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
- `python manage.py telegram_poll` — legge i messaggi Telegram in arrivo e
  collega gli account allievo che inviano `/link <codice>` dal portale.
  Pensato per girare ogni 1-2 minuti da cron; non fa nulla se
  `TELEGRAM_BOT_TOKEN` non è configurato.

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

## Notifiche Telegram e WhatsApp

Entrambi sono canali opzionali e aggiuntivi rispetto all'email, ciascuno con
il proprio interruttore in `/admin/core/impostazioni/` (entrambi disattivati
di default):

- **Telegram** è pienamente funzionante: crea un bot con
  [@BotFather](https://t.me/BotFather), metti il token in
  `TELEGRAM_BOT_TOKEN` nel `.env`, attivalo in Impostazioni e programma
  `telegram_poll` da cron. Gli allievi collegano l'account da soli dal
  portale (nessun webhook necessario — il server non ha bisogno di un IP
  pubblico, interroga lui Telegram periodicamente).
- **WhatsApp** è predisposto per la Meta WhatsApp Business Cloud API
  (`WHATSAPP_ACCESS_TOKEN` / `WHATSAPP_PHONE_NUMBER_ID` nel `.env`) ma non è
  mai stato provato contro un account reale — richiede un account Meta
  Business verificato che questo progetto non può fornire. Rivedi
  `comunicazioni/canali/whatsapp.py` prima di farci affidamento.

## Ruoli e accesso

- **Admin/segreteria** (superuser): accesso completo, incluso `/admin/`.
- **Istruttori** (gruppo "Istruttori", `is_staff=True`): gestione completa di
  lezioni/partecipazioni, sola lettura su allievi/cavalli/campi/pacchetti,
  nessun accesso ai documenti riservati (certificati, dati sensibili).
- **Allievi/genitori** (gruppo "Allievi", `is_staff=False`): nessun accesso
  admin, portale in `/persone/portale/` con le proprie lezioni e lo stato
  del pacchetto. Se l'amministratore attiva l'opzione "Prenotazione autonoma"
  (in `/admin/core/impostazioni/`, **disattivata di default**), possono anche
  prenotare/annullare da soli la propria partecipazione a lezioni con posti
  liberi — il cavallo resta comunque assegnato dalla segreteria.

## App

| App | Responsabilità |
|---|---|
| `core` | home page, login/logout, cornice del sito, impostazioni globali |
| `persone` | allievi, tutori, istruttori, proprietari, documenti, portale allievi |
| `cavalli` | anagrafica cavalli (scuola/pensione) |
| `lezioni` | campi, tipi lezione, calendario, form lezione/partecipazioni, prenotazione autonoma |
| `pacchetti` | tipi di pacchetto configurabili, pacchetti acquistati |
| `comunicazioni` | promemoria/alert (email, Telegram, WhatsApp), broadcast |
| `report` | presenze/assenze, utilizzo cavalli, occupazione istruttori/campi, scadenze |

## Switch di lingua (italiano/inglese)

L'app ha uno switch di lingua in navbar (italiano e inglese), basato sull'i18n
standard di Django via sessione — nessun prefisso negli URL, quindi i link
già esistenti (compresi quelli incorporati nei QR delle tessere digitali)
continuano a funzionare a prescindere dalla lingua. Copertura: navigazione,
pulsanti, titoli e messaggi delle view sui template principali. **Non ancora
tradotti**: le etichette dei campi e le scelte dei modelli nell'admin di
Django (es. nomi dei tipi di lezione/pacchetto) — l'admin resta
volutamente solo in italiano per ora, visto che l'uso quotidiano dello staff
è in italiano; è un limite noto, non una svista.

Le traduzioni vivono in `locale/en/LC_MESSAGES/django.po` (+ `django.mo`
compilato). Normalmente si rigenererebbero con `makemessages`/
`compilemessages` di Django, ma richiedono il pacchetto di sistema `gettext`
(`xgettext`/`msgfmt`), che potrebbe non essere disponibile ovunque senza
accesso root. Se non ce l'hai nemmeno tu, `locale/genera_traduzioni.py`
genera `.po`/`.mo` direttamente con `polib` (puro Python, nessun pacchetto di
sistema) a partire da un dizionario di stringhe mantenuto a mano — aggiorna
quel dizionario e rilancia lo script quando aggiungi nuovo testo traducibile.
Se `gettext` **è** disponibile sul tuo sistema, usa pure i comandi standard
di Django al suo posto.

## Fuori scope (deciso esplicitamente)

- Pagamenti/fatturazione: nessun incasso tracciato in nessun punto del
  sistema (i pacchetti hanno solo un prezzo di riferimento informativo).
- Lista d'attesa automatica per le lezioni: con i numeri di un centro
  ippico tipico si gestisce a voce più in fretta di quanto costerebbe
  costruirla e mantenerla.
- Tracciamento di un livello/progressione tecnica dell'allievo: EquiLesson
  registra solo la propensione verso un tipo di lezione, non una valutazione
  di competenza.
- Regole rigide di preavviso disdetta: a discrezione della segreteria, il
  sistema non le impone.
- Piattaforma multi-tenant centralizzata: ogni installazione è indipendente
  (vedi "Adottarlo per il tuo maneggio").

## Roadmap

**MVP (completo):**

1. ~~Ruoli e permessi~~ ✅
2. ~~Calendario lezioni~~ ✅
3. ~~Portale allievi/genitori~~ ✅
4. ~~Notifiche/comunicazioni~~ ✅
5. ~~Report~~ ✅

**Fase 2 (in corso), nata da un confronto con altri gestionali del settore:**

- [x] Prenotazione autonoma allievi, attivabile/disattivabile dall'admin
- [x] Notifiche Telegram (WhatsApp predisposto, non verificato)
- [ ] Scadenze sanitarie strutturate per i cavalli (vaccinazioni, ferrature, sverminazioni) con promemoria automatico
- [ ] Export dei report in CSV/PDF
- [ ] Portale di sola lettura per i proprietari di cavalli in pensione
- [ ] Consenso privacy/liberatoria con tracciamento di accettazione (data, non solo una checkbox)
- [ ] Tessera digitale con QR per gli allievi
- [x] Interfaccia bilingue italiano/inglese (template e messaggi delle view; etichette admin ancora solo in italiano)

Estensioni future possibili (non bloccanti): rifinitura estetica dedicata,
gestione gare/eventi, piano alimentare cavallo, magazzino/tack room, app
mobile, check-in su tablet, fatturazione, sito web pubblico del centro.

## Adottarlo per il tuo maneggio

Il modello di distribuzione è **un'installazione indipendente per ogni
centro** (niente multi-tenant, niente dati di più maneggi nello stesso
database): ogni struttura ha una propria copia, configurabile nei tipi di
lezione, nei tagli di pacchetto, nei campi, ecc. Puoi clonare il repo e
installarlo da solo seguendo la sezione "Setup sviluppo" qui sopra (per la
produzione serve in più un database Postgres dedicato e un reverse proxy con
HTTPS davanti a Django — non ancora documentato in dettaglio in questo repo).

**Ti piace il progetto?** Il codice resta gratuito sotto AGPL-3.0: puoi
scaricarlo e farlo girare da solo senza dovermi nulla. Se preferisci non
occupartene tu — installazione sul tuo server, configurazione su misura per
il tuo centro, migrazione dei dati esistenti, assistenza continuativa — è un
servizio a pagamento: apri una issue o scrivi a dragonknigth09@gmail.com. Il
progetto resta gratis, il mio tempo no.

## Licenza

Distribuito sotto [GNU AGPL-3.0](LICENSE). In breve: puoi usare, modificare e
ridistribuire liberamente il codice, anche a scopo commerciale, ma se lo
usi per far girare un servizio raggiungibile via rete (anche solo per un
singolo maneggio, non necessariamente in vendita) devi rendere disponibile
il codice sorgente completo — comprese le tue modifiche — a chi usa quel
servizio. Non è richiesta alcuna condizione simile per il solo uso interno
senza esporlo ad altri via rete.

## Sicurezza

Il sistema tratta dati sensibili (certificati medici, dati di minorenni).
Per segnalare una vulnerabilità in modo responsabile vedi [SECURITY.md](SECURITY.md).

## Contribuire

Contributi, segnalazioni di bug e proposte sono benvenuti: vedi
[CONTRIBUTING.md](CONTRIBUTING.md).
