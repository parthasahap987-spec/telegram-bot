import logging
import requests
from bs4 import BeautifulSoup
from telegram import Update
from telegram.ext import Updater, MessageHandler, Filters, CallbackContext

# 🔑 CONFIG
BOT_TOKEN = "8763433771:AAE5N47qKXfmtkCOMRct0tC6tn1l9YtpaZs"
CHANNEL_ID = -1002161382456
AFFILIATE_TAG = "partha07e-21"

logging.basicConfig(level=logging.INFO)

# 🔗 Affiliate link
def make_affiliate(url):
    if "tag=" in url:
        return url
    if "?" in url:
        return url + "&tag=" + AFFILIATE_TAG
    else:
        return url + "?tag=" + AFFILIATE_TAG

# 📦 Scraper
def get_data(url):
    headers = {"User-Agent": "Mozilla/5.0"}

    r = requests.get(url, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")

    # 💰 Price
    price = soup.select_one(".a-price-whole")
    price = price.text.strip() if price else "N/A"

    # 🔥 Discount
    discount = soup.select_one(".savingsPercentage")
    discount = discount.text.strip() if discount else "N/A"

    # 🖼️ Image
    img = soup.find("img", {"id": "landingImage"})
    img_url = img["src"] if img else None

    return price, discount, img_url

# 🤖 Handler
def handle(update: Update, context: CallbackContext):
    url = update.message.text

    if "amazon" not in url:
        update.message.reply_text("❌ Send Amazon link only")
        return

    price, discount, img = get_data(url)
    aff = make_affiliate(url)

    caption = f"""💰 ₹{price}
🔥 {discount}

👉 Buy Now: {aff}"""

    try:
        if img:
            context.bot.send_photo(CHANNEL_ID, img, caption=caption)
        else:
            context.bot.send_message(CHANNEL_ID, caption)

        update.message.reply_text("✅ Posted")

    except Exception as e:
        update.message.reply_text(f"Error: {e}")

# 🚀 Run
def main():
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle))

    print("Bot Running 🚀")
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
