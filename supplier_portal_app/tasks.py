import frappe
from .bank_connector.psd2_client import BankAPIConnector

@frappe.whitelist()
def sync_bank_transactions_and_fees():
    configs = frappe.get_all("Bank API Config", filters={"enabled": 1}, fields=["name"])
    for cfg in configs:
        try:
            _process_bank_config(cfg.name)
        except Exception as e:
            frappe.log_error(f"Bank sync error [{cfg.name}]: {e}", "Bank Sync")


def _process_bank_config(config_name):
    connector = BankAPIConnector(config_name)
    config_doc = frappe.get_doc("Bank API Config", config_name)
    for account in config_doc.bank_accounts:
        transactions = connector.fetch_transactions(account.external_account_id)
        for tx in transactions:
            _upsert_bank_transaction(tx, account, config_doc)


def _upsert_bank_transaction(tx, account, config):
    tx_id = tx.get("transactionId") or tx.get("entryReference")
    if frappe.db.exists("Bank Transaction", {"transaction_id": tx_id}):
        return

    amount = float(tx["transactionAmount"]["amount"])
    direction = "Entrata" if amount > 0 else "Uscita"

    bt = frappe.get_doc({
        "doctype": "Bank Transaction",
        "date": tx.get("bookingDate"),
        "transaction_id": tx_id,
        "bank_account": account.bank_account,
        "deposit": abs(amount) if direction == "Entrata" else 0,
        "withdrawal": abs(amount) if direction == "Uscita" else 0,
        "description": tx.get("remittanceInformationUnstructured", ""),
        "currency": tx["transactionAmount"]["currency"]
    }).insert(ignore_permissions=True)

    fee_rule = get_fee_rule(direction, abs(amount), account.bank_account)
    if fee_rule:
        fee_amount = abs(amount) * (fee_rule.percentage / 100)
        fee_amount = max(fee_amount, fee_rule.minimum_fee or 0)
        frappe.get_doc({
            "doctype": "Transaction Fee",
            "transaction_id": tx_id,
            "bank_account": account.bank_account,
            "transaction_date": tx.get("bookingDate"),
            "amount": abs(amount),
            "fee_percentage": fee_rule.percentage,
            "fee_amount": fee_amount,
            "direction": direction,
            "status": "Pending",
            "bank_transaction": bt.name
        }).insert(ignore_permissions=True)

    frappe.db.commit()


def get_fee_rule(direction, amount, bank_account):
    rules = frappe.get_all(
        "Fee Rule",
        filters={
            "direction": direction,
            "bank_account": ["in", [bank_account, ""]],
            "enabled": 1,
            "min_amount": ["<=", amount]
        },
        fields=["name", "percentage", "minimum_fee"],
        order_by="min_amount desc",
        limit=1
    )
    return frappe.get_doc("Fee Rule", rules[0].name) if rules else None
