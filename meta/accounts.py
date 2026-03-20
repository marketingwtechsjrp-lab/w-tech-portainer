"""
Gerenciamento de contas de clientes Meta Ads.
As contas ficam salvas em accounts.json no diretório do projeto.
"""
import json
import os
from pathlib import Path
from typing import Optional

ACCOUNTS_FILE = Path(__file__).parent / "accounts.json"


def _load_accounts() -> dict:
    if not ACCOUNTS_FILE.exists():
        return {}
    with open(ACCOUNTS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def _save_accounts(accounts: dict) -> None:
    with open(ACCOUNTS_FILE, "w", encoding="utf-8") as f:
        json.dump(accounts, f, indent=2, ensure_ascii=False)


def add_account(
    slug: str,
    name: str,
    access_token: str,
    ad_account_id: str,
    notes: str = "",
    niche: str = "custom",
) -> None:
    """Cadastra ou atualiza uma conta de cliente."""
    accounts = _load_accounts()
    # Garante formato act_XXXX
    if not ad_account_id.startswith("act_"):
        ad_account_id = f"act_{ad_account_id}"
    accounts[slug] = {
        "name": name,
        "access_token": access_token,
        "ad_account_id": ad_account_id,
        "notes": notes,
        "niche": niche,
    }
    _save_accounts(accounts)


def remove_account(slug: str) -> bool:
    accounts = _load_accounts()
    if slug not in accounts:
        return False
    del accounts[slug]
    _save_accounts(accounts)
    return True


def list_accounts() -> dict:
    return _load_accounts()


def get_account(slug: str) -> Optional[dict]:
    accounts = _load_accounts()
    return accounts.get(slug)


def update_account(slug: str, **fields) -> bool:
    """Atualiza campos de uma conta existente."""
    accounts = _load_accounts()
    if slug not in accounts:
        return False
    for key, val in fields.items():
        if val is not None:
            if key == "ad_account_id" and not val.startswith("act_"):
                val = f"act_{val}"
            accounts[slug][key] = val
    _save_accounts(accounts)
    return True


def get_account_credentials(slug: str) -> Optional[dict]:
    """Retorna access_token e ad_account_id para uso na API."""
    account = get_account(slug)
    if not account:
        return None
    return {
        "access_token": account["access_token"],
        "ad_account_id": account["ad_account_id"],
        "name": account["name"],
        "niche": account.get("niche", "custom"),
    }
