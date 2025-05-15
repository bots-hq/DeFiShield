import re
from telegram import Update
from telegram.ext import CallbackContext
from parser_dexscreener import get_contract_details
from parser_goplus import get_additional_details

def handle_message(update: Update, context: CallbackContext):
    text = update.message.text
    match = re.search(r'0x[a-fA-F0-9]{40}', text)
    if not match:
        return

    contract_address = match.group(0).lower()
    details = get_contract_details(contract_address)
    additional = get_additional_details(contract_address)

    if not details or not additional:
        update.message.reply_text("Unable to fetch contract details.")
        return

    top_holders = ' | '.join(
        f"{round(float(h['percent']) * 100, 2)}%" for h in additional['top_holders']
    )
    creator_percent = round(float(additional.get('creator_percent') or 0) * 100, 2)
    dexs_link = f"https://dexscreener.com/{details['chain_id']}/{contract_address}"

    message = (
        f"🔷 <b>{additional['token_name']} ({additional['token_symbol']})</b>\n"
        f"<b>Website:</b> <a href='{details['website']}'>Link</a>\n"
        f"<b>Liquidity:</b> ${details['liquidity']}\n"
        f"<b>Price:</b> ${details['price_usd']}\n"
        f"<b>Top Holders:</b> {top_holders}\n"
        f"<b>DEX Screener:</b> <a href='{dexs_link}'>View</a>\n"
    )
    update.message.reply_html(message)
