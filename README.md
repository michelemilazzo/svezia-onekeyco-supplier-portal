# svezia-onekeyco-supplier-portal

ERPNext custom app per la gestione del portale fornitori, fatturazione entrata/uscita, fee sulle transazioni e integrazione con bank API.

## Cosa include
- DocType `Transaction Fee` per fee transazionali
- DocType `Fee Rule` per regole fee basate su soglia e direzione
- DocType `Bank API Config` per configurare connessioni PSD2/Open Banking
- Integrazione iniziale con Revolut e Andaria
- Scheduler per sincronizzazione transazioni e calcolo fee
- Hook per generare automaticamente fatture da fee approvate

## Installazione
```bash
cd /path/to/bench/apps
git clone https://github.com/michelemilazzo/svezia-onekeyco-supplier-portal.git
bench --site yoursite install-app supplier_portal_app
bench --site yoursite migrate
```

## Note
Questo repository è generato automaticamente e contiene lo scheletro dell'app con i principali componenti richiesti. Il modulo andrà adattato all'installazione ERPNext specifica e completato con i connettori della banca e i workflow.
