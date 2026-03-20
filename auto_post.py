import re
import requests
from bs4 import BeautifulSoup
from telegram import Bot, Update
from telegram.ext import Updater, MessageHandler, Filters, CallbackContext

# 🔑 CONFIG
BOT_TOKEN = "8542006683:AAF0x8hzY0G1XWI39GbV9T5rdf8eeyamD18"
CHANNEL_ID = -1002161382456
AFFILIATE_TAG = "partha07e-21"

bot = Bot(token=BOT_TOKEN)

# 🔗 Affiliate link add
def add_tag(url):
    if "tag=" in url:
        return url
    if "?" in url:
        return url + "&tag=" + AFFILIATE_TAG
    else:
        return url + "?tag=" + AFFILIATE_TAG

# 🔄 Short link expand
def expand_url(url):
    try:
        return requests.get(url, allow_redirects=True, timeout=10).url
    except:
        return url

# 📦 Scraper (FIXED)
def get_data(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Linux; Android 10)",
        "Accept-Language": "en-US,en;q=0.9"
    }

    try:
        r = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")

        # 💰 PRICE
        price = "Check"
        tag = soup.select_one(".a-price-whole")
        if tag:
            price = tag.get_text().strip()

        # 🔥 DISCOUNT
        discount = "Offer"
        tag = soup.select_one(".savingsPercentage")
        if tag:
            discount = tag.get_text().strip()

        # 🖼 IMAGE
        img = None
        tag = soup.find("img", {"id": "landingImage"})
        if tag:
            img = tag.get("src")

        return price, discount, img

    except Exception as e:
        print(e)
        return "Check", "Offer", None

# 🤖 MAIN HANDLER
def handle(update: Update, context: CallbackContext):
    text = update.message.text

    links = re.findall(r'https?://\S+', text)
    if not links:
        update.message.reply_text("❌ Send Amazon link")
        return

    url = links[0]

    # 🔄 Short link support
    if "amzn.to" in url:
        url = expand_url(url)

    # 🔗 Affiliate add
    aff_link = add_tag(url)

    try:
        price, discount, img = get_data(url)

        caption = f"""💰 Price: ₹{price}
🔥 Discount: {discount}

👉 Buy Now:
{aff_link}
"""

        # 📸 Send post
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

# 🚀 RUN
def main():
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle))

    print("Bot Running 🚀")
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
