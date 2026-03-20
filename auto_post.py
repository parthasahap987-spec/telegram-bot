import re
import requests
from telegram import Update
from telegram.ext import Updater, MessageHandler, Filters, CallbackContext

# 🔑 CONFIG
BOT_TOKEN = "8798520446:AAGIWH8Cli7c-l2nc_dbG3mgn70BUYNmmUY"
CHANNEL_ID = -1002161382456
AFFILIATE_TAG = "partha07e-21"

# 🔗 make clean affiliate link (NO EXTRA TAG)
def make_affiliate(url):
    try:
        # remove all params
        base = url.split("?")[0]
        return base + "?tag=" + AFFILIATE_TAG
    except:
        return url

# 🔄 expand short link
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
        msg.reply_text("❌ No text")
        return

    # 🔍 সব link detect
    links = re.findall(r'https?://[^\s]+', text)

    if not links:
        msg.reply_text("❌ No link found")
        return

    # 👉 প্রথম link use করবো
    original_link = links[0]

    # 🔄 short link expand
    if "amzn.to" in original_link:
        original_link = expand_url(original_link)

    # 🔗 final affiliate link
    aff_link = make_affiliate(original_link)

    # ❌ সব link remove
    clean_text = re.sub(r'https?://[^\s]+', '', text).strip()

    # ➕ শেষে নিজের link add
    final_text = f"{clean_text}\n\n👉 Buy Now:\n{aff_link}"

    try:
        # 📸 image থাকলে
        if msg.photo:
            context.bot.send_photo(
                chat_id=CHANNEL_ID,
                photo=msg.photo[-1].file_id,
                caption=final_text,
                disable_web_page_preview=True
            )
        else:
            context.bot.send_message(
                chat_id=CHANNEL_ID,
                text=final_text,
                disable_web_page_preview=True
            )

        msg.reply_text("✅ Done (Only your affiliate link added)")

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
