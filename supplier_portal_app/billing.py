import frappe


def on_fee_approved(doc, method):
    if doc.direction == "Entrata":
        _create_sales_invoice_from_fee(doc)
    else:
        _create_purchase_invoice_from_fee(doc)


def _create_sales_invoice_from_fee(fee_doc):
    sinv = frappe.get_doc({
        "doctype": "Sales Invoice",
        "customer": fee_doc.customer or "",
        "posting_date": fee_doc.transaction_date,
        "due_date": fee_doc.transaction_date,
        "items": [{
            "item_code": "FEE-SERVICE",
            "description": f"Fee transazione {fee_doc.transaction_id}",
            "qty": 1,
            "rate": fee_doc.fee_amount,
            "income_account": fee_doc.income_account or "Ricavi Transazioni - AZIENDA"
        }],
        "custom_transaction_fee": fee_doc.name
    })
    sinv.insert(ignore_permissions=True)
    sinv.submit()
    fee_doc.db_set("status", "Invoiced")
    fee_doc.db_set("sales_invoice", sinv.name)


def _create_purchase_invoice_from_fee(fee_doc):
    pinv = frappe.get_doc({
        "doctype": "Purchase Invoice",
        "supplier": fee_doc.supplier or "",
        "posting_date": fee_doc.transaction_date,
        "due_date": fee_doc.transaction_date,
        "items": [{
            "item_code": "FEE-SERVICE",
            "description": f"Fee transazione {fee_doc.transaction_id}",
            "qty": 1,
            "rate": fee_doc.fee_amount,
            "expense_account": fee_doc.expense_account or "Fee Bancarie - AZIENDA"
        }],
        "custom_transaction_fee": fee_doc.name
    })
    pinv.insert(ignore_permissions=True)
    pinv.submit()
    fee_doc.db_set("status", "Invoiced")
    fee_doc.db_set("purchase_invoice", pinv.name)
