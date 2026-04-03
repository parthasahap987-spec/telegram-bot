import re
import requests
from telegram import Update
from telegram.ext import Updater, MessageHandler, Filters, CallbackContext

BOT_TOKEN = "8645119625:AAHLcrsVzJzaBwsSRAO3OIoXFlUAVwnrmr8"
CHANNEL_ID = -1002161382456
AFFILIATE_TAG = "partha07e-21"


# 🔗 Affiliate বানানো
def make_affiliate(url):
    try:
        url = re.sub(r'([&?])tag=[^&]+', '', url)
        if "?" in url:
            return url + "&tag=" + AFFILIATE_TAG
        else:
            return url + "?tag=" + AFFILIATE_TAG
    except:
        return url


# 🔁 Short link expand
def expand_url(url):
    try:
        return requests.get(url, allow_redirects=True, timeout=10).url
    except:
        return url


# 🖼 Amazon image scrape
def get_amazon_image(url):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0"
        }
        res = requests.get(url, headers=headers, timeout=10)
        html = res.text

        # og:image detect
        match = re.search(r'<meta property="og:image" content="([^"]+)"', html)
        if match:
            return match.group(1)

    except:
        return None

    return None


# 🤖 MAIN HANDLER
def handle(update: Update, context: CallbackContext):
    msg = update.message

    text = msg.caption if msg.caption else msg.text
    if not text:
        return

    found_links = []

    # 🔄 Replace links
    def replace_link(match):
        link = match.group(0)

        if any(x in link for x in ["amazon.", "amzn.to"]):

            if "amzn.to" in link:
                link = expand_url(link)

            aff = make_affiliate(link)
            found_links.append(aff)
            return aff

        return link

    new_text = re.sub(r'https?://[^\s]+', replace_link, text)

    try:
        # 📩 STEP 1: Text send
        sent_msg = context.bot.send_message(
            chat_id=CHANNEL_ID,
            text=new_text,
            disable_web_page_preview=False
        )

        # 📸 STEP 2: Image send (reply)
        if msg.photo:
            context.bot.send_photo(
                chat_id=CHANNEL_ID,
                photo=msg.photo[-1].file_id,
                reply_to_message_id=sent_msg.message_id
            )

        else:
            # 🔍 Amazon থেকে image আনা
            for link in found_links:
                img = get_amazon_image(link)
                if img:
                    context.bot.send_photo(
                        chat_id=CHANNEL_ID,
                        photo=img,
                        reply_to_message_id=sent_msg.message_id
                    )
                    break

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
