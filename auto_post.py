import re
import requests
from telegram import Update
from telegram.ext import Updater, MessageHandler, Filters, CallbackContext

BOT_TOKEN = "8645119625:AAHLcrsVzJzaBwsSRAO3OIoXFlUAVwnrmr8"
CHANNEL_ID = -1002161382456
AFFILIATE_TAG = "partha07e-21"

def make_affiliate(url):
    try:
        base = url.split("?")[0]
        return base + "?tag=" + AFFILIATE_TAG
    except:
        return url

def expand_url(url):
    try:
        return requests.get(url, allow_redirects=True, timeout=10).url
    except:
        return url

# 🤖 HANDLER
def handle(update: Update, context: CallbackContext):
    msg = update.message

    text = msg.caption if msg.caption else msg.text
    if not text:
        return

    # 🔁 function for replacing each link
    def replace_link(match):
        link = match.group(0)

        # 👉 only Amazon
        if "amazon" in link or "amzn.to" in link:

            if "amzn.to" in link:
                link = expand_url(link)

            return make_affiliate(link)

        return link  # অন্য link untouched থাকবে

    # 🔄 inline replace
    new_text = re.sub(r'https?://[^\s]+', replace_link, text)

    try:
        # 📸 image থাকলে
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

    except Exception as e:
        print("Error:", e)

# 🚀 RUN
def main():
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(MessageHandler(Filters.all, handle))

    print("Bot Running 🚀")
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
