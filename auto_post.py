import re
import requests
from bs4 import BeautifulSoup
from telegram import Bot
from telegram.ext import Updater, MessageHandler, Filters

BOT_TOKEN = "8659070537:AAG-O3aN5rGAdtnkINkn3eaoTlkrs8CO2NI"
CHANNEL = -1002161382456
AFFILIATE_TAG = "partha07e-21"

bot = Bot(token=BOT_TOKEN)

def add_tag(url):
    if "amazon" in url:
        if "?" in url:
            return url + "&tag=" + AFFILIATE_TAG
        else:
            return url + "?tag=" + AFFILIATE_TAG
    return url

def get_data(url):
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept-Language": "en-US,en;q=0.9"
    }

    r = requests.get(url, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")

    # Price
    price = "Check"
    tag = soup.select_one(".a-price .a-offscreen")
    if tag:
        price = tag.get_text().replace("₹", "").strip()

    # Discount
    discount = "Offer"
    tag = soup.select_one(".savingsPercentage")
    if tag:
        discount = tag.get_text().strip()

    # Image
    img = None
    tag = soup.find("img", {"id": "landingImage"})
    if tag:
        img = tag.get("src")

    if img and not img.startswith("http"):
        img = None

    return price, discount, img

def handle(update, context):
    text = update.message.text
    links = re.findall(r'https?://\S+', text)

    if not links:
        return

    url = links[0]
    aff_link = add_tag(url)

    price, discount, img = get_data(url)

    caption = "💰 ₹" + price + "\n🏷️ " + discount + "\n" + aff_link
    caption = caption[:1000]

    try:
        if img:
            bot.send_photo(chat_id=CHANNEL, photo=img, caption=caption)
        else:
            bot.send_message(chat_id=CHANNEL, text=caption, disable_web_page_preview=True)

        update.message.reply_text("✅ Done")

    except Exception as e:
        update.message.reply_text(str(e))

updater = Updater(BOT_TOKEN, use_context=True)
dp = updater.dispatcher
dp.add_handler(MessageHandler(Filters.text, handle))

print("Bot Running 🚀")
updater.start_polling()
updater.idle()
