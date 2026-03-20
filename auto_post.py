import re
import requests
from telegram import Update
from telegram.ext import Updater, MessageHandler, Filters, CallbackContext

BOT_TOKEN = "8645119625:AAFyZsv5UHsKSmoWk3oDsD-Umzh44fZS5kw"
CHANNEL_ID = -1002161382456
API_KEY = "8Nbk30Vhmnq49-N_12i7TImcX42kSFfR8Q3pyOKHmVc"

# 🔄 expand short link
def expand_url(url):
    try:
        return requests.get(url, allow_redirects=True, timeout=10).url
    except:
        return url

# 🔗 cuelinks convert (DEBUG)
def convert_cuelinks(url):
    try:
        api = f"https://api.cuelinks.com/link?url={url}&key={API_KEY}"
        r = requests.get(api, timeout=10)
        data = r.json()

        print("API RESPONSE:", data)  # 🔥 debug

        if "shortUrl" in data:
            return data["shortUrl"]

        # ❗ fallback (force change)
        return "https://linksredirect.com/?url=" + url

    except Exception as e:
        print("API ERROR:", e)
        return "https://linksredirect.com/?url=" + url


def handle(update: Update, context: CallbackContext):
    msg = update.message
    text = msg.caption if msg.caption else msg.text

    if not text:
        msg.reply_text("❌ No text")
        return

    # 🔍 detect links (strong regex)
    links = re.findall(r'https?://[^\s]+', text)

    if not links:
        msg.reply_text("❌ No link found")
        return

    new_text = text

    for link in links:
        clean_link = link.strip()

        # 🔄 expand short
        if "amzn.to" in clean_link:
            clean_link = expand_url(clean_link)

        # 🔗 convert
        aff = convert_cuelinks(clean_link)

        # 🔁 replace safely
        new_text = new_text.replace(link, aff)

    try:
        if msg.photo:
            context.bot.send_photo(
                chat_id=CHANNEL_ID,
                photo=msg.photo[-1].file_id,
                caption=new_text,
                disable_web_page_preview=True
            )
        else:
            context.bot.send_message(
                chat_id=CHANNEL_ID,
                text=new_text,
                disable_web_page_preview=True
            )

        msg.reply_text("✅ Converted (Force Mode)")

    except Exception as e:
        msg.reply_text(f"❌ Error: {e}")


def main():
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(MessageHandler(Filters.all, handle))

    print("Bot Running 🚀")
    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
