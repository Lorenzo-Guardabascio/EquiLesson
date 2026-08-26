# Contribuire a EquiLesson

Grazie per l'interesse! Il progetto è giovane e mantenuto part-time da una
sola persona, quindi i tempi di risposta possono essere lenti — non è
disattenzione, è normale amministrazione delle priorità.

## Segnalare un bug

Apri una issue con:

- cosa ti aspettavi che succedesse e cosa è successo davvero;
- passi per riprodurlo, se possibile;
- versione di Django/Python e sistema operativo, se rilevante.

Se il bug riguarda dati sensibili (certificati medici, dati di minorenni) o è
una vulnerabilità di sicurezza, **non aprire una issue pubblica**: segui
invece [SECURITY.md](SECURITY.md).

## Proporre una modifica

1. Apri prima una issue per discutere il cambiamento se è più di una
   correzione puntuale (nuova funzionalità, cambio di schema dati,
   modifica di uno scope già deciso) — evita di scrivere molto codice che
   poi non viene accettato perché va in una direzione diversa da quella del
   progetto.
2. Fai fork e crea un branch descrittivo (`feature/...`, `fix/...`).
3. Segui lo stile del codice esistente: modelli/campi/commit message in
   italiano (dominio del progetto), codice/nomi Python idiomatici, verbose
   che rispecchiano il dominio (es. `Allievo`, `Lezione`, non `Student`,
   `Lesson`).
4. `python manage.py check` deve passare senza errori prima di aprire la PR.
5. Descrivi nella PR cosa cambia e perché, non solo il "come".

## Scope del progetto

Prima di proporre una funzionalità, controlla la sezione "Fuori scope" nel
[README](README.md#fuori-scope-deciso-esplicitamente): alcune esclusioni
(pagamenti/fatturazione, prenotazione autonoma degli allievi, lista d'attesa)
sono scelte deliberate per questo progetto, non dimenticanze.

## Licenza dei contributi

Contribuendo accetti che il tuo codice venga distribuito sotto la stessa
licenza del progetto ([AGPL-3.0](LICENSE)).
