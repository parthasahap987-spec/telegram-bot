import re
import requests
from telegram import Update
from telegram.ext import Updater, MessageHandler, Filters, CallbackContext

BOT_TOKEN = "NEW_TOKEN_DAO"   # 🔴 নতুন token use করো
CHANNEL_ID = -1002161382456
AFFILIATE_TAG = "partha07e-21"

# 🔗 Affiliate বানানো (improved)
def make_affiliate(url):
    try:
        # ❗ আগে পুরনো tag remove
        url = re.sub(r'([&?])tag=[^&]+', '', url)

        # ❗ clean শেষ ? বা &
        if "?" in url:
            return url + "&tag=" + AFFILIATE_TAG
        else:
            return url + "?tag=" + AFFILIATE_TAG

    except:
        return url


# 🔁 Short link expand (STRONG VERSION)
def expand_url(url):
    try:
        session = requests.Session()
        session.headers.update({
            "User-Agent": "Mozilla/5.0"
        })
        res = session.get(url, allow_redirects=True, timeout=10)
        return res.url
    except:
        return url


# 🤖 MAIN HANDLER
def handle(update: Update, context: CallbackContext):
    msg = update.message

    text = msg.caption if msg.caption else msg.text
    if not text:
        return

    # 🔄 Replace links
    def replace_link(match):
        link = match.group(0)

        # 👉 Amazon detect (STRONG)
        if any(x in link for x in ["amazon.", "amzn.to"]):

            # 🔁 expand short link
            if "amzn.to" in link:
                link = expand_url(link)

            # 🔗 affiliate add
            return make_affiliate(link)

        return link

    new_text = re.sub(r'https?://[^\s]+', replace_link, text)

    try:
        # 📸 IMAGE FIX (ALL TYPES)
        if msg.photo:
            context.bot.send_photo(
                chat_id=CHANNEL_ID,
                photo=msg.photo[-1].file_id
            )

            context.bot.send_message(
                chat_id=CHANNEL_ID,
                text=new_text,
                disable_web_page_preview=True
            )

        elif msg.document and msg.document.mime_type.startswith("image"):
            context.bot.send_document(
                chat_id=CHANNEL_ID,
                document=msg.document.file_id
            )

            context.bot.send_message(
                chat_id=CHANNEL_ID,
                text=new_text,
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
