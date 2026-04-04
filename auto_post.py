import re
import requests
import io
from telegram import Update
from telegram.ext import Updater, MessageHandler, Filters, CallbackContext

BOT_TOKEN = "8645119625:AAEnBkJ5ND1z06BS9ui4YX_nkFJ8kwLgFY0"
CHANNEL_ID = -1002161382456
AFFILIATE_TAG = "partha07e-21"


# 🔁 Expand ANY short link
def expand_url(url):
    try:
        session = requests.Session()
        session.headers.update({"User-Agent": "Mozilla/5.0"})
        res = session.get(url, allow_redirects=True, timeout=10)
        return res.url
    except:
        return url


# 🔗 Clean Amazon affiliate link (FIXED)
def make_affiliate(url):
    try:
        match = re.search(r'(https://www\.amazon\.[^/]+/dp/[A-Z0-9]+)', url)

        if match:
            clean_url = match.group(1)
        else:
            clean_url = url.split("?")[0]

        return clean_url + "?tag=" + AFFILIATE_TAG

    except:
        return url


# 🖼 Get Amazon image
def get_amazon_image(url):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0",
            "Accept-Language": "en-US,en;q=0.9"
        }

        html = requests.get(url, headers=headers, timeout=10).text

        patterns = [
            r'<meta property="og:image" content="([^"]+)"',
            r'"hiRes":"([^"]+)"',
            r'"large":"([^"]+)"',
            r'"mainUrl":"([^"]+)"'
        ]

        for p in patterns:
            match = re.search(p, html)
            if match:
                img = match.group(1)
                img = img.replace("\\u0026", "&").replace("\\", "")
                if img.startswith("http"):
                    return img

    except:
        pass

    return None


# 📸 Send image (download → upload fix)
def send_image(context, chat_id, img_url, caption):
    try:
        res = requests.get(img_url, stream=True, timeout=10)
        if res.status_code == 200:
            image_bytes = io.BytesIO(res.content)
            image_bytes.name = "product.jpg"

            context.bot.send_photo(
                chat_id=chat_id,
                photo=image_bytes,
                caption=caption,
                disable_web_page_preview=True
            )
            return True
    except:
        return False

    return False


# 🤖 Auto format পোস্ট
def format_post(text, affiliate_link):
    lines = text.split("\n")

    product = ""
    price = ""
    offers = []

    for line in lines:
        l = line.lower()

        if "₹" in line or "rs" in l:
            price = line.strip()

        elif "off" in l or "coupon" in l or "card" in l:
            offers.append("✔ " + line.strip())

        elif len(line) > 20 and not product:
            product = line.strip()

    if not product:
        product = lines[0]

    if not price:
        price = "Best Price Available"

    if not offers:
        offers = ["✔ Extra Discount Available"]

    offer_text = "\n".join(offers)

    final = f"""🔥 DEAL ALERT 🔥

💥 Grab Now 💥

🛒 {product}
💰 {price}

🎯 Offers:
{offer_text}

👉 BUY NOW 👇  
{affiliate_link}

⚡ Hurry! Limited Time Deal"""

    return final[:1000]


# 🤖 MAIN HANDLER
def handle(update: Update, context: CallbackContext):
    msg = update.message

    # ✅ TEXT FIX (caption priority)
    text = ""
    if msg.caption:
        text = msg.caption
    elif msg.text:
        text = msg.text

    if text.strip() == "":
        return

    found_links = []

    def replace_link(match):
        link = match.group(0)

        # 🔥 detect all amazon links
        if any(x in link for x in ["amazon.", "amzn"]):

            if "amzn" in link:
                link = expand_url(link)

            aff = make_affiliate(link)
            found_links.append(aff)
            return aff

        return link

    new_text = re.sub(r'https?://[^\s]+', replace_link, text)

    try:
        affiliate_link = found_links[0] if found_links else ""

        final_post = format_post(new_text, affiliate_link)

        image_sent = False

        # ✅ PHOTO
        if msg.photo:
            context.bot.send_photo(
                chat_id=CHANNEL_ID,
                photo=msg.photo[-1].file_id,
                caption=final_post,
                disable_web_page_preview=True
            )
            image_sent = True

        # ✅ DOCUMENT IMAGE
        elif msg.document and msg.document.mime_type and msg.document.mime_type.startswith("image"):
            context.bot.send_photo(
                chat_id=CHANNEL_ID,
                photo=msg.document.file_id,
                caption=final_post,
                disable_web_page_preview=True
            )
            image_sent = True

        # ✅ AMAZON IMAGE FETCH
        if not image_sent:
            for link in found_links:
                img = get_amazon_image(link)
                if img:
                    if send_image(context, CHANNEL_ID, img, final_post):
                        image_sent = True
                        break

        # ✅ FALLBACK TEXT
        if not image_sent:
            context.bot.send_message(
                chat_id=CHANNEL_ID,
                text=final_post,
                disable_web_page_preview=True
            )

    except Exception as e:
        print("Error:", e)


# 🚀 RUN
def main():
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(MessageHandler(
        Filters.text | Filters.caption | Filters.photo | Filters.document,
        handle
    ))

    print("Bot Running 🚀")
    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
