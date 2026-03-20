import re
import requests
from telegram import Update
from telegram.ext import Updater, MessageHandler, Filters, CallbackContext

# 🔑 CONFIG
BOT_TOKEN = "8645119625:AAFyZsv5UHsKSmoWk3oDsD-Umzh44fZS5kw"
CHANNEL_ID = -1002161382456

# 👉 CUELINKS API KEY
API_KEY = "8Nbk30Vhmnq49-N_12i7TImcX42kSFfR8Q3pyOKHmVc"

# 🔄 Expand short link
def expand_url(url):
    try:
        return requests.get(url, allow_redirects=True, timeout=10).url
    except:
        return url

# 🔗 Convert to Cuelinks
def convert_cuelinks(url):
    try:
        api_url = f"https://api.cuelinks.com/link?url={url}&key={API_KEY}"
        res = requests.get(api_url, timeout=10).json()

        if "shortUrl" in res:
            return res["shortUrl"]

        return url
    except:
        return url

# 🤖 HANDLER
def handle(update: Update, context: CallbackContext):
    msg = update.message

    text = msg.caption if msg.caption else msg.text
    if not text:
        msg.reply_text("❌ No text found")
        return

    # 🔍 detect ALL links
    links = re.findall(r'https?://[^\s]+', text)

    if not links:
        msg.reply_text("❌ No link found")
        return

    new_text = text

    for link in links:
        final_link = link

        # 🔄 expand short
        if "amzn.to" in link:
            final_link = expand_url(link)

        # 🔗 convert affiliate
        aff_link = convert_cuelinks(final_link)

        # 🔁 replace each link
        new_text = new_text.replace(link, aff_link)

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

        msg.reply_text("✅ All links converted & posted")

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
