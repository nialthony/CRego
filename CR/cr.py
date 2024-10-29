import telebot
import requests
import re
import time

# Replace with your bot's API token and required channel invite link
API_TOKEN = '5749873566:AAFPBH4E3BkmxSmDios6seIEBvDFc1taDNk'
CHANNEL_INVITE_LINK = '@cekrego'  # Replace with your channel invite link
bot = telebot.TeleBot(API_TOKEN)

# Known popular cryptocurrencies
POPULAR_CRYPTO_IDS = {
    'btc': 'bitcoin',
    'eth': 'ethereum',
    'trx': 'tron',
    'ltc': 'litecoin',
    'xrp': 'ripple',
    'doge': 'dogecoin',
    'degen': 'degen-base',
    'apt': 'aptos',
    'eos': 'eos',
    'dot': 'polkadot',
    'usdt': 'tether',
    'bnb': 'binancecoin',
    'ada': 'cardano',
    'shib': 'shiba-inu',
    'bch': 'bitcoin-cash',
    'pepe': 'pepe',
    'sei': 'sei-network',
    'sol': 'solana',
    'ton': 'the-open-network',
    'arb': 'arbitrum',
    'cet': 'coinex-token',
    'pol': 'polygon-ecosystem-token',
    'cati': 'catizen',
    # Add more popular crypto IDs as needed
}

# Fetch all available crypto IDs, symbols, and names from CoinGecko
def fetch_crypto_symbols():
    url = "https://api.coingecko.com/api/v3/coins/list"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        symbol_to_id = {}
        id_to_symbol = {}
        id_to_name = {}  # New dictionary to store names

        for item in data:
            symbol = item['symbol'].lower()
            coin_id = item['id']
            coin_name = item['name']  # Fetch the name

            # If the symbol is in the POPULAR_CRYPTO_IDS, use the known ID
            if symbol in POPULAR_CRYPTO_IDS:
                symbol_to_id[symbol] = POPULAR_CRYPTO_IDS[symbol]
            else:
                symbol_to_id[symbol] = coin_id

            # Store the symbol in uppercase and name for response formatting
            id_to_symbol[coin_id] = symbol.upper()
            id_to_name[coin_id] = coin_name  # Store the name

        return symbol_to_id, id_to_symbol, id_to_name
    return {}, {}, {}

# Load crypto symbols, symbols, and names on startup
CRYPTO_SYMBOLS_TO_ID, ID_TO_CRYPTO_SYMBOL, ID_TO_CRYPTO_NAME = fetch_crypto_symbols()

# Helper function to get cryptocurrency prices and 24h change
def get_crypto_price_and_change(crypto_id, vs_currencies):
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={crypto_id}&vs_currencies={vs_currencies}&include_24hr_change=true"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    return None

# Function to check if a user is a member of the channel
def is_user_member(user_id):
    try:
        time.sleep(1)  # Add a delay before checking membership
        chat_member = bot.get_chat_member(CHANNEL_INVITE_LINK, user_id)
        return chat_member.status in ('member', 'administrator', 'creator')
    except telebot.apihelper.ApiException as e:
        print(f"Error checking membership: {str(e)}")
        return False
    except Exception as e:
        print(f"Error checking membership: {str(e)}")
        return False

# Helper function to parse amounts with abbreviations like "rb" and "jt"
def parse_amount(amount_str):
    amount_str = amount_str.lower().replace(" ", "")
    if 'jt' in amount_str:
        return float(amount_str.replace('jt', '').replace(',', '.')) * 1_000_000
    elif 'rb' in amount_str:
        return float(amount_str.replace('rb', '').replace(',', '.')) * 1_000
    else:
        return float(amount_str.replace(',', '.'))

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    reply_text = (
        "\n\nSelamat datang sluurr di Cek Rego Crypto Bot!\n"
        "> Command:\n"
        "> Convert IDR ke Crypto:\n"
        "> `50000 idr trx`, `50rb idr doge`,\n"
        "> `1jt idr sol`, `2.4jt idr sol`, dll.\n"
        "> Hitung Crypto ke USD dan IDR:\n"
        "> `1.3 eth`, `0.95 sol`, dll.\n\n"
        "> Bot masih dalam proses pengembangan fitur......\n\n\n\n\n\n\n\n"
        "Donate pliss :D\n"
        "> Solana: `6XMtN9fr4cn4Q669S26JbMVwcxkTFcP6sbEeYcbnB1nD`\n"
        "> ETH/EVM: `0x25FF09C0d3D5961c771D96aA2Ad5a3fBEfDce1a6`\n"
        "Sing nggawe bot: @nialthony"
    )
    
    # Escaping characters for MarkdownV2
    reply_text = reply_text.replace('.', r'\.').replace('-', r'\-').replace('!', r'\!')

    bot.reply_to(message, reply_text, parse_mode='MarkdownV2')

# Function to process messages
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    text = message.text.lower()

    # Define the regex pattern to match messages like "1 btc" or "1.34jt idr eth"
    pattern_crypto = r"^\d+(\.\d+)?\s+\w+$"  # Pattern for crypto commands
    pattern_fiat = r"^\d+(\.\d+)?\s*(rb|jt)?\s*\w+\s+\w+$"  # Pattern for fiat to crypto commands

    # Check if the message matches the pattern for crypto conversion
    if re.match(pattern_crypto, text):
        user_id = message.from_user.id

        # Check if the user is a member of the required channel
        if not is_user_member(user_id):
            bot.reply_to(message, f"Koe kudu join {CHANNEL_INVITE_LINK} supoyo isoh nganggo bot iki.")
            return

        tokens = text.split()
        amount = float(tokens[0])
        user_symbol = tokens[1]

        # Convert the user-friendly symbol to the CoinGecko ID
        crypto_id = CRYPTO_SYMBOLS_TO_ID.get(user_symbol)

        if crypto_id:
            vs_currencies = 'usd,idr'
            price_data = get_crypto_price_and_change(crypto_id, vs_currencies)

            if price_data and crypto_id in price_data:
                prices = price_data[crypto_id]

                # Get the correct symbol and name from ID_TO_CRYPTO_SYMBOL and ID_TO_CRYPTO_NAME
                correct_symbol = ID_TO_CRYPTO_SYMBOL.get(crypto_id, user_symbol.upper())
                crypto_name = ID_TO_CRYPTO_NAME.get(crypto_id, crypto_id)

                # Determine if 24-hour change should be shown
                show_change = amount == 1.0
                change_text = ""
                if show_change:
                    usd_change = prices.get('usd_24h_change', None)
                    idr_change = prices.get('idr_24h_change', None)
                    if usd_change is not None or idr_change is not None:
                        change_text = f"| {usd_change:+.2f}% 24h "

                # Build the response message in monotype font
                response = f"```\n{amount} {correct_symbol} ({crypto_name}) {change_text}:\n\n"
                for currency, price in prices.items():
                    if "24h_change" in currency:
                        continue
                    converted_amount = amount * price
                    response += f"{converted_amount:,.2f} {currency.upper()}\n"
                response += "```"

                bot.reply_to(message, response, parse_mode='MarkdownV2')
            else:
                bot.reply_to(message, f"Afatuh {user_symbol.upper()} ?")
        else:
            bot.reply_to(message, f"Afaan tuh '{user_symbol.upper()}' ?")
    
    # Check if the message matches the pattern for fiat to crypto conversion
    elif re.match(pattern_fiat, text):
        user_id = message.from_user.id

        # Check if the user is a member of the required channel
        if not is_user_member(user_id):
            bot.reply_to(message, f"You must join {CHANNEL_INVITE_LINK} to use this bot.")
            return

        tokens = re.split(r'\s+', text)  # Split the text with any whitespace
        amount_str = tokens[0]
        fiat_currency = tokens[-2]
        user_symbol = tokens[-1]

        amount = parse_amount(amount_str)

        # Convert the user-friendly symbol to the CoinGecko ID
        crypto_id = CRYPTO_SYMBOLS_TO_ID.get(user_symbol)
        crypto_name = ID_TO_CRYPTO_NAME.get(crypto_id, crypto_id)

        if crypto_id:
            vs_currencies = fiat_currency
            price_data = get_crypto_price_and_change(crypto_id, vs_currencies)

            if price_data and crypto_id in price_data:
                prices = price_data[crypto_id]
                fiat_price = prices.get(fiat_currency, None)

                if fiat_price:
                    crypto_amount = amount / fiat_price
                    correct_symbol = ID_TO_CRYPTO_SYMBOL.get(crypto_id, user_symbol.upper())
                    crypto_name = ID_TO_CRYPTO_NAME.get(crypto_id, crypto_id)

                    response = f"```\n{amount:,.2f} {fiat_currency.upper()} =\n\n {crypto_amount:.6f} {correct_symbol} ({crypto_name})\n```"
                    bot.reply_to(message, response, parse_mode='MarkdownV2')
                else:
                    bot.reply_to(message, f"Sorry, I couldn't find the price for {fiat_currency.upper()} to {user_symbol.upper()}.")
            else:
                bot.reply_to(message, f"Afatuh {user_symbol.upper()} ?")
        else:
            bot.reply_to(message, f"Afaan tuh, '{user_symbol.upper()}' ?")
    
    else:
        # Ignore any message that doesn't match the pattern
        pass

if __name__ == "__main__":
    # Start the bot's main loop with auto-reconnect
    while True:
        try:
            bot.polling(none_stop=True, interval=0)
        except Exception as e:
            print(f"An error occurred: {str(e)}")
