import os
import re
import requests
from datetime import datetime
from telegram import Update, Bot
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# Replace 'YOUR_TELEGRAM_BOT_TOKEN' with your actual bot token
TELEGRAM_BOT_TOKEN = '7455487097:AAFSHIwJmY7Pmk2_SRRCkspoRsZy1_pwS8s'

# Function to fetch contract details from DexScreener
def get_contract_details(contract_address):
    url = f"https://api.dexscreener.com/latest/dex/search/?q={contract_address}"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        pairs = data.get("pairs", [])
        if pairs:
            pair = pairs[0]  # Assuming only one pair is returned
            chain_id = pair.get("chainId")
            price_usd = pair.get("priceUsd")
            fdv = pair.get("fdv")
            liquidity = pair.get("liquidity", {}).get("usd")
            volume_24h = pair.get("volume", {}).get("h24")
            buys_24h = pair.get("txns", {}).get("h24", {}).get("buys")
            sells_24h = pair.get("txns", {}).get("h24", {}).get("sells")
            price_change_24h = pair.get("priceChange", {}).get("h24")
            price_change_6h = pair.get("priceChange", {}).get("h6")
            
            # Calculate age of the pair
            pair_created_timestamp = pair.get("pairCreatedAt")
            if pair_created_timestamp:
                pair_created_date = datetime.fromtimestamp(pair_created_timestamp / 1000)
                age_days = (datetime.now() - pair_created_date).days
                age_str = f"{age_days} days ago"
            else:
                age_str = "N/A"
            
            # Extract social and website info
            socials = pair.get("info", {}).get("socials", [])
            website = next((site['url'] for site in pair.get("info", {}).get("websites", []) if site['label'] == "Website"), "N/A")
            twitter = next((social['url'] for social in socials if social['type'] == "twitter"), "N/A")
            telegram = next((social['url'] for social in socials if social['type'] == "telegram"), "N/A")

            return {
                "chain_id": chain_id,
                "price_usd": price_usd,
                "fdv": fdv,
                "liquidity": liquidity,
                "volume_24h": volume_24h,
                "buys_24h": buys_24h,
                "sells_24h": sells_24h,
                "price_change_24h": price_change_24h,
                "price_change_6h": price_change_6h,
                "age_str": age_str,
                "website": website,
                "twitter": twitter,
                "telegram": telegram
            }
        else:
            return None
    else:
        return None

# Function to fetch additional contract details from GoPlusLabs
def get_additional_details(contract_address):
    url = f"https://api.gopluslabs.io/api/v1/token_security/8453?contract_addresses={contract_address}"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        result = data.get("result", {}).get(contract_address, {})
        
        creator_percent = result.get("creator_percent")
        creator_address = result.get("creator_address")
        holder_count = result.get("holder_count")
        top_holders = [
            {"address": holder["address"], "percent": holder["percent"]}
            for holder in result.get("holders", [])
            if not holder.get("is_contract") and not holder.get("is_locked")
        ][:3]
        honeypot_with_same_creator = "YES" if result.get("honeypot_with_same_creator") == "1" else "NO"
        is_anti_whale = "YES" if result.get("is_anti_whale") == "1" else "NO"
        is_blacklisted = "YES" if result.get("is_blacklisted") == "1" else "NO"
        is_honeypot = "YES" if result.get("is_honeypot") == "1" else "NO"
        owner_address = result.get("owner_address")
        slippage_modifiable = "YES" if result.get("slippage_modifiable") == "1" else "NO"
        token_name = result.get("token_name")
        token_symbol = result.get("token_symbol")
        total_supply = result.get("total_supply")
        trading_cooldown = result.get("trading_cooldown")
        buy_tax = result.get("buy_tax")
        sell_tax = result.get("sell_tax")
        cannot_sell_all = "YES" if result.get("cannot_sell_all") == "1" else "NO"
        
        return {
            "creator_percent": creator_percent,
            "creator_address": creator_address,
            "holder_count": holder_count,
            "top_holders": top_holders,
            "honeypot_with_same_creator": honeypot_with_same_creator,
            "is_anti_whale": is_anti_whale,
            "is_blacklisted": is_blacklisted,
            "is_honeypot": is_honeypot,
            "owner_address": owner_address,
            "slippage_modifiable": slippage_modifiable,
            "token_name": token_name,
            "token_symbol": token_symbol,
            "total_supply": total_supply,
            "trading_cooldown": trading_cooldown,
            "buy_tax": buy_tax,
            "sell_tax": sell_tax,
            "cannot_sell_all": cannot_sell_all
        }
    else:
        return None

# Function to handle incoming messages
def handle_message(update: Update, context: CallbackContext):
    message_text = update.message.text
    
    # Check if the message contains an Ethereum contract address
    match = re.search(r'0x[a-fA-F0-9]{40}', message_text)
    if match:
        contract_address = match.group(0).lower()
       
        details = get_contract_details(contract_address)
        additional_details = get_additional_details(contract_address)
        if details and additional_details:
            # Extract and format top holders' percentages
            top_holders_percent = ' | '.join(
                f"{round(float(holder['percent']) * 100, 2)}%" 
                for holder in additional_details['top_holders'][:3] 
                if not holder.get('is_contract') and not holder.get('is_locked')
            )
            # Handle creator percent with a default value if None
            creator_percent = additional_details.get('creator_percent', 0)
            creator_percent = round(float(creator_percent) * 100, 2) if creator_percent is not None else 0
            # Create the details message with HTML formatting
            dexs_link = f"https://dexscreener.com/{details['chain_id']}/{contract_address}"
            dext_link = f"https://dextools.io"
            details_message = (
    f"🔷 <b>{additional_details['token_name']} ({additional_details['token_symbol']})</b>\n"
    f"🔗 <a href='https://t.me/TonOnBase_TONB'>TONB Guardian Report</a>\n\n"
    
    f"<b>🌍 Social Links:</b> "
    f"<a href='{details['website']}'>Website</a> | "
    f"<a href='{details['telegram']}'>Telegram</a> | "
    f"<a href='{details['twitter']}'>Twitter</a>\n\n"
    
    f"<b>💡 Overview:</b>\n"
    f"• <b>Age:</b> {details['age_str']}\n"
    f"• <b>Chain ID:</b> {details['chain_id']}\n"
    f"• <b>Price (USD):</b> ${details['price_usd']}\n"
    f"• <b>Fully Diluted Valuation (FDV):</b> ${details['fdv']}\n"
    f"• <b>Total Supply:</b> {additional_details['total_supply']}\n"
    f"• <b>Liquidity (USD):</b> ${details['liquidity']}\n\n"
    
    f"<b>📊 Market Activity:</b>\n"
    f"• <b>24h Volume:</b> ${details['volume_24h']}\n"
    f"• <b>24h Buys:</b> {details['buys_24h']}\n"
    f"• <b>24h Sells:</b> {details['sells_24h']}\n"
    f"• <b>6h Price Change:</b> {details['price_change_6h']}%\n"
    f"• <b>24h Price Change:</b> {details['price_change_24h']}%\n\n"
    
    f"<b>⚙️ Creator & Holders:</b>\n"
    f"• <b>Creator Address:</b> {additional_details['creator_address']}\n"
    f"• <b>Creator Holding:</b> {creator_percent}%\n"
    f"• <b>Top 3 Holders:</b> {top_holders_percent}%\n"
    f"• <b>Total Holders:</b> {additional_details['holder_count']}\n\n"
    
    f"<b>🔒 Security Checks:</b>\n"
    f"• <b>Honeypot with Same Creator:</b> {'🚩 YES' if additional_details['honeypot_with_same_creator'] == '1' else '✅ NO'}\n"
    f"• <b>Anti-Whale:</b> {'✅ YES' if additional_details['is_anti_whale'] == '1' else '🚩 NO'}\n"
    f"• <b>Blacklist Function:</b> {'🚩 YES' if additional_details['is_blacklisted'] == '1' else '✅ NO'}\n"
    f"• <b>Honeypot Risk:</b> {'🚩 YES' if additional_details['is_honeypot'] == '1' else '✅ NO'}\n"
    f"• <b>Ownership Renounced:</b> {'✅ YES' if additional_details['owner_address'] == '0x0000000000000000000000000000000000000000' else '🚩 NO'}\n"
    f"• <b>Slippage Modifiable:</b> {'🚩 YES' if additional_details['slippage_modifiable'] == '1' else '✅ NO'}\n"
    f"• <b>Trading Cooldown:</b> {'🚩 YES' if additional_details['trading_cooldown'] == '1' else '✅ NO'}\n"
    f"• <b>Cannot Sell All:</b> {'🚩 YES' if additional_details['cannot_sell_all'] == '1' else '✅ NO'}\n\n"
    
    f"<b>📈 Additional Resources:</b>\n"
    f"🔍 <a href='{dexs_link}'>View on DexS</a>"
)

            # Send the message
            update.message.reply_html(details_message)

        else:
            update.message.reply_text("Unable to fetch contract details.")
    else:
        pass

def main():
    updater = Updater(TELEGRAM_BOT_TOKEN, use_context=True)
    dp = updater.dispatcher
    
    # Add message handler
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))
    
    # Start the bot
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
