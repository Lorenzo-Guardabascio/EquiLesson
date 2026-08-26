# Security Policy

EquiLesson gestisce dati sensibili: certificati medici, dati di minorenni,
documenti d'identità/tesseramento. Prendiamo sul serio le segnalazioni di
sicurezza.

## Segnalare una vulnerabilità

**Non aprire una issue pubblica.** Scrivi invece direttamente a
dragonknigth09@gmail.com descrivendo:

- il tipo di vulnerabilità e il suo impatto potenziale;
- i passi per riprodurla;
- versione/commit del progetto interessato.

Riceverai una risposta appena possibile. Ti chiediamo di darci un tempo
ragionevole per pubblicare una correzione prima di divulgare i dettagli
pubblicamente (responsible disclosure).

## Versioni supportate

Il progetto non ha ancora release versionate: le correzioni di sicurezza
vengono applicate sul branch principale.

## Ambito

Rientrano in questo ambito: autenticazione/autorizzazione, accesso ai
documenti riservati (`persone.Documento`), portale allievi, esposizione di
dati personali (allievi minorenni, dati sanitari) tra ruoli diversi da
quello previsto. Non rientrano: assenza di funzionalità (es. mancanza di
2FA) — quelle si propongono come issue normali, non come segnalazioni di
sicurezza.
