# Svezia OneKeyCo Supplier Portal

Frappe / ERPNext app for the OneKeyCo Sweden supplier portal.

## Scope

This app provides a supplier and banking fee workflow for ERPNext:

- Supplier invoice fee workflow
- PSD2 / bank API transaction synchronization
- Transaction fee rules
- Fee approval flow
- Sales Invoice / Purchase Invoice generation from approved transaction fees

## Target compatibility

- Frappe Framework: v16
- ERPNext: v16
- Python: >=3.11,<3.13

## Required apps

- frappe
- erpnext

## Install on a Frappe bench

```bash
cd /path/to/frappe-bench
bench get-app https://github.com/michelemilazzo/svezia-onekeyco-supplier-portal.git
bench --site your-site.local install-app supplier_portal_app
bench --site your-site.local migrate
bench --site your-site.local clear-cache
```

## Main DocTypes

The app defines these custom DocTypes:

- Bank API Config
- Bank API Account
- Fee Rule
- Transaction Fee

The app also adds custom links on ERPNext documents:

- Sales Invoice: `custom_transaction_fee`
- Purchase Invoice: `custom_transaction_fee`

## Notes for MMOS / Press

The `main` branch is the single operational branch for the Frappe / ERPNext v16 compatibility baseline.

Recommended test:

```bash
bench --site test.local install-app supplier_portal_app
bench --site test.local migrate
bench --site test.local execute supplier_portal_app.tasks.sync_bank_transactions_and_fees
```
