import requests
from datetime import datetime

def get_contract_details(contract_address):
    url = f"https://api.dexscreener.com/latest/dex/search/?q={contract_address}"
    response = requests.get(url)

    if response.status_code != 200:
        return None

    data = response.json()
    pairs = data.get("pairs", [])
    if not pairs:
        return None

    pair = pairs[0]
    pair_created_timestamp = pair.get("pairCreatedAt")
    age_str = "N/A"
    if pair_created_timestamp:
        age_days = (datetime.now() - datetime.fromtimestamp(pair_created_timestamp / 1000)).days
        age_str = f"{age_days} days ago"

    info = pair.get("info", {})
    socials = info.get("socials", [])
    website = next((site['url'] for site in info.get("websites", []) if site['label'] == "Website"), "N/A")
    twitter = next((s['url'] for s in socials if s['type'] == "twitter"), "N/A")
    telegram = next((s['url'] for s in socials if s['type'] == "telegram"), "N/A")

    return {
        "chain_id": pair.get("chainId"),
        "price_usd": pair.get("priceUsd"),
        "fdv": pair.get("fdv"),
        "liquidity": pair.get("liquidity", {}).get("usd"),
        "volume_24h": pair.get("volume", {}).get("h24"),
        "buys_24h": pair.get("txns", {}).get("h24", {}).get("buys"),
        "sells_24h": pair.get("txns", {}).get("h24", {}).get("sells"),
        "price_change_24h": pair.get("priceChange", {}).get("h24"),
        "price_change_6h": pair.get("priceChange", {}).get("h6"),
        "age_str": age_str,
        "website": website,
        "twitter": twitter,
        "telegram": telegram
    }
