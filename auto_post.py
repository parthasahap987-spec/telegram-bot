import re
import requests
from telegram import Update
from telegram.ext import Updater, MessageHandler, Filters, CallbackContext

# 🔑 CONFIG
BOT_TOKEN = "8799971120:AAHlHlFBghuS73mBBaUI27PA1Ih45f1NhCw"
CHANNEL_ID = -1002161382456
AFFILIATE_TAG = "partha07e-21"

# 🔗 Affiliate add
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

# 🤖 HANDLER
def handle(update: Update, context: CallbackContext):
    msg = update.message

    # 👉 caption বা text ধরো
    text = msg.caption if msg.caption else msg.text
    if not text:
        msg.reply_text("❌ No text found")
        return

    # 🔍 link detect
    links = re.findall(r'https?://\S+', text)
    if not links:
        msg.reply_text("❌ No link found")
        return

    original_link = links[0]

    # 🔄 expand short link
    if "amzn.to" in original_link:
        original_link = expand_url(original_link)

    # 🔗 affiliate বানাও
    aff_link = add_tag(original_link)

    # 🔁 replace link
    new_text = text.replace(links[0], aff_link)

    try:
        # 📸 যদি image থাকে
        if msg.photo:
            photo = msg.photo[-1].file_id

            context.bot.send_photo(
                chat_id=CHANNEL_ID,
                photo=photo,
                caption=new_text,
                disable_web_page_preview=True
            )

        # 📄 যদি শুধু text হয়
        else:
            context.bot.send_message(
                chat_id=CHANNEL_ID,
                text=new_text,
                disable_web_page_preview=True
            )

        msg.reply_text("✅ Posted with affiliate link")

    except Exception as e:
        msg.reply_text(f"❌ Error: {e}")

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
