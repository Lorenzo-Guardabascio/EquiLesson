[🇮🇹 Italiano](README.md) · 🇬🇧 English

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
| `core` | home page, login/logout, site frame |
| `persone` | students, guardians, instructors, horse owners, documents, student portal |
| `cavalli` | horse records (school horses / boarders) |
| `lezioni` | arenas, lesson types, calendar, lesson/participation form |
| `pacchetti` | configurable package types, purchased packages |
| `comunicazioni` | automatic reminders/alerts, broadcasts (via admin) |
| `report` | attendance, horse usage, instructor/arena occupancy, expiries |

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
- [ ] Telegram and WhatsApp notifications, in addition to email
- [ ] Structured health-due-dates for horses (vaccinations, farrier visits,
      deworming) with automatic reminders
- [ ] CSV/PDF export for reports
- [ ] Read-only portal for boarding-horse owners
- [ ] Privacy/liability consent with tracked acceptance (a timestamp, not
      just a checkbox)
- [ ] Digital membership card with QR code for students
- [ ] Bilingual Italian/English interface

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
