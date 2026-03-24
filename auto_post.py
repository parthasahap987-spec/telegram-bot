import re
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

BOT_TOKEN = "8645119625:AAFyZsv5UHsKSmoWk3oDsD-Umzh44fZS5kw"
CHANNEL_ID = -1002161382456
AFFILIATE_TAG = "partha07e-21"

# 🔗 affiliate link
def make_affiliate(url):
    try:
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

# 🖼️ Amazon product image extract
def get_amazon_image(url):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0"
        }
        r = requests.get(url, headers=headers, timeout=10)
        html = r.text

        # og:image meta tag extract
        match = re.search(r'<meta property="og:image" content="([^"]+)"', html)
        if match:
            return match.group(1)

    except:
        return None

    return None

# 🤖 handler
async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message

    text = msg.caption if msg.caption else msg.text
    if not text:
        return

    links = re.findall(r'https?://[^\s]+', text)

    if not links:
        return

    final_links = []
    image_url = None

    for link in links:

        if "amazon" in link or "amzn.to" in link:

            if "amzn.to" in link:
                link = expand_url(link)

            aff = make_affiliate(link)
            final_links.append(aff)

            # 👉 প্রথম link থেকে image আনবো (if needed)
            if not image_url:
                image_url = get_amazon_image(link)

    if not final_links:
        return

    clean_text = re.sub(r'https?://[^\s]+', '', text).strip()
    links_text = "\n".join(final_links)

    final_text = f"{clean_text}\n\n👉 Buy Now:\n{links_text}"

    try:
        # 📸 Case 1: original image থাকলে সেটাই use
        if msg.photo:
            await context.bot.send_photo(
                chat_id=CHANNEL_ID,
                photo=msg.photo[-1].file_id,
                caption=final_text,
                disable_web_page_preview=True
            )

        # 📸 Case 2: image নাই → Amazon থেকে image আনবো
        elif image_url:
            await context.bot.send_photo(
                chat_id=CHANNEL_ID,
                photo=image_url,
                caption=final_text,
                disable_web_page_preview=True
            )

        # ❌ fallback → text only
        else:
            await context.bot.send_message(
                chat_id=CHANNEL_ID,
                text=final_text,
                disable_web_page_preview=True
            )

    except Exception as e:
        print("Error:", e)

# 🚀 run
app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(MessageHandler(filters.ALL, handle))

print("Bot Running 🚀")
app.run_polling()
