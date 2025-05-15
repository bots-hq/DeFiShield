import requests

def get_additional_details(contract_address):
    url = f"https://api.gopluslabs.io/api/v1/token_security/8453?contract_addresses={contract_address}"
    response = requests.get(url)

    if response.status_code != 200:
        return None

    result = response.json().get("result", {}).get(contract_address, {})
    top_holders = [
        {"address": h["address"], "percent": h["percent"]}
        for h in result.get("holders", [])
        if not h.get("is_contract") and not h.get("is_locked")
    ][:3]

    return {
        "creator_percent": result.get("creator_percent"),
        "creator_address": result.get("creator_address"),
        "holder_count": result.get("holder_count"),
        "top_holders": top_holders,
        "honeypot_with_same_creator": result.get("honeypot_with_same_creator"),
        "is_anti_whale": result.get("is_anti_whale"),
        "is_blacklisted": result.get("is_blacklisted"),
        "is_honeypot": result.get("is_honeypot"),
        "owner_address": result.get("owner_address"),
        "slippage_modifiable": result.get("slippage_modifiable"),
        "token_name": result.get("token_name"),
        "token_symbol": result.get("token_symbol"),
        "total_supply": result.get("total_supply"),
        "trading_cooldown": result.get("trading_cooldown"),
        "buy_tax": result.get("buy_tax"),
        "sell_tax": result.get("sell_tax"),
        "cannot_sell_all": result.get("cannot_sell_all")
    }
