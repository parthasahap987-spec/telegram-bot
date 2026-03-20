import logging
import requests
import re
from bs4 import BeautifulSoup
from telegram import Update
from telegram.ext import Updater, MessageHandler, Filters, CallbackContext

# 🔑 CONFIG
BOT_TOKEN = "8542006683:AAF0x8hzY0G1XWI39GbV9T5rdf8eeyamD18"
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

# 🔄 Short link expand (amzn.to)
def expand_url(url):
    try:
        r = requests.get(url, allow_redirects=True, timeout=10)
        return r.url
    except:
        return url

# 📦 Scrape Amazon
def get_data(url):
    headers = {"User-Agent": "Mozilla/5.0"}

    r = requests.get(url, headers=headers, timeout=10)
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
    text = update.message.text

    # 🔍 Extract URL from any text
    urls = re.findall(r'https?://\S+', text)
    if not urls:
        update.message.reply_text("❌ Send Amazon link")
        return

    url = urls[0]

    # 🔄 Expand short link
    if "amzn.to" in url:
        url = expand_url(url)

    # 🔗 Affiliate link
    aff = make_affiliate(url)

    try:
        price, discount, img = get_data(url)

        caption = f"""💰 ₹{price}
🔥 {discount}

👉 Buy Now: {aff}"""

        if img:
            context.bot.send_photo(
                chat_id=CHANNEL_ID,
                photo=img,
                caption=caption,
                disable_web_page_preview=True
            )
        else:
            context.bot.send_message(
                chat_id=CHANNEL_ID,
                text=caption,
                disable_web_page_preview=True
            )

        update.message.reply_text("✅ Posted")

    except Exception as e:
        update.message.reply_text(f"❌ Error: {e}")

# 🚀 Run bot
def main():
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle))

    print("Bot Running 🚀")
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
