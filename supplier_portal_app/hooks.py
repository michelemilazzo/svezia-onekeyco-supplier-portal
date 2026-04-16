from .tasks import sync_bank_transactions_and_fees
from .billing import on_fee_approved

app_name = "supplier_portal_app"
app_title = "Supplier Portal App"
app_publisher = "OneKeyCo"
app_description = "ERPNext app for supplier invoice portal, bank API integration, fees and reconciliation."
app_icon = "octicon octicon-file-directory"
app_color = "grey"
app_email = "support@onekeyco.com"
app_license = "MIT"

scheduler_events = {
    "hourly": [
        "supplier_portal_app.tasks.sync_bank_transactions_and_fees"
    ]
}

doc_events = {
    "Transaction Fee": {
        "on_submit": "supplier_portal_app.billing.on_fee_approved"
    }
}
