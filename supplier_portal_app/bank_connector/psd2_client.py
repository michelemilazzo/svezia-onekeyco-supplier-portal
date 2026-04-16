import frappe
import requests
import base64
import hashlib
import secrets
from datetime import datetime, timedelta


class BankAPIConnector:
    def __init__(self, bank_config_name):
        self.config = frappe.get_doc("Bank API Config", bank_config_name)
        self.base_url = self.config.api_base_url

    def authenticate_device(self):
        code_verifier = secrets.token_urlsafe(64)
        digest = hashlib.sha256(code_verifier.encode()).digest()
        code_challenge = base64.urlsafe_b64encode(digest).rstrip(b"=").decode()
        frappe.cache().set_value(f"pkce_{self.config.name}", code_verifier, expires_in_sec=300)
        auth_url = (
            f"{self.base_url}/oauth/authorize"
            f"?response_type=code"
            f"&client_id={self.config.client_id}"
            f"&redirect_uri={self.config.redirect_uri}"
            f"&scope=accounts transactions payments"
            f"&code_challenge={code_challenge}"
            f"&code_challenge_method=S256"
        )
        return auth_url

    def exchange_code_for_token(self, auth_code):
        code_verifier = frappe.cache().get_value(f"pkce_{self.config.name}")
        resp = requests.post(f"{self.base_url}/oauth/token", data={
            "grant_type": "authorization_code",
            "code": auth_code,
            "redirect_uri": self.config.redirect_uri,
            "client_id": self.config.client_id,
            "client_secret": self.config.get_password("client_secret"),
            "code_verifier": code_verifier,
        })
        resp.raise_for_status()
        token_data = resp.json()
        self.config.db_set("access_token", token_data["access_token"])
        self.config.db_set("refresh_token", token_data["refresh_token"])
        self.config.db_set("token_expiry", datetime.now() + timedelta(seconds=token_data["expires_in"]))
        return token_data

    def _get_valid_token(self):
        expiry = self.config.token_expiry
        if expiry and datetime.now() < expiry - timedelta(minutes=5):
            return self.config.access_token
        resp = requests.post(f"{self.base_url}/oauth/token", data={
            "grant_type": "refresh_token",
            "refresh_token": self.config.refresh_token,
            "client_id": self.config.client_id,
            "client_secret": self.config.get_password("client_secret"),
        })
        resp.raise_for_status()
        new_tokens = resp.json()
        self.config.db_set("access_token", new_tokens["access_token"])
        self.config.db_set("refresh_token", new_tokens.get("refresh_token", self.config.refresh_token))
        self.config.db_set("token_expiry", datetime.now() + timedelta(seconds=new_tokens["expires_in"]))
        return new_tokens["access_token"]

    def fetch_transactions(self, account_id, date_from=None, date_to=None):
        token = self._get_valid_token()
        headers = {
            "Authorization": f"Bearer {token}",
            "X-Request-ID": frappe.generate_hash(length=16),
        }
        params = {
            "dateFrom": (date_from or (datetime.now() - timedelta(days=1))).strftime("%Y-%m-%d"),
            "dateTo": (date_to or datetime.now()).strftime("%Y-%m-%d"),
            "bookingStatus": "booked",
        }
        resp = requests.get(
            f"{self.base_url}/v1/accounts/{account_id}/transactions",
            headers=headers,
            params=params,
        )
        resp.raise_for_status()
        return resp.json().get("transactions", {}).get("booked", [])

    def initiate_payment(self, payment_data):
        token = self._get_valid_token()
        headers = {
            "Authorization": f"Bearer {token}",
            "X-Request-ID": frappe.generate_hash(length=16),
        }
        resp = requests.post(
            f"{self.base_url}/v1/payments/sepa-credit-transfers",
            headers=headers,
            json={
                "instructedAmount": {
                    "currency": payment_data["currency"],
                    "amount": str(payment_data["amount"]),
                },
                "debtorAccount": {"iban": payment_data["debtor_iban"]},
                "creditorAccount": {"iban": payment_data["creditor_iban"]},
                "creditorName": payment_data["creditor_name"],
                "remittanceInformationUnstructured": payment_data.get("reference", ""),
            },
        )
        resp.raise_for_status()
        result = resp.json()
        if result.get("_links", {}).get("scaRedirect"):
            return {
                "status": "SCA_REQUIRED",
                "redirect_url": result["_links"]["scaRedirect"]["href"],
                "payment_id": result["paymentId"],
            }
        return {"status": result["transactionStatus"], "payment_id": result["paymentId"]}
