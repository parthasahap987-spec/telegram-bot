import re
import requests
from telegram import Update
from telegram.ext import Updater, MessageHandler, Filters, CallbackContext

BOT_TOKEN = "8645119625:AAHLcrsVzJzaBwsSRAO3OIoXFlUAVwnrmr8"
CHANNEL_ID = -1002161382456
AFFILIATE_TAG = "partha07e-21"


# 🔁 Short link expand
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


# 🔗 Affiliate link বানানো
def make_affiliate(url):
    try:
        url = re.sub(r'([&?])tag=[^&]+', '', url)
        url = re.sub(r'([&?])(ref|psc|smid|linkCode|th)=[^&]+', '', url)
        url = url.rstrip("?&")

        if "?" in url:
            return url + "&tag=" + AFFILIATE_TAG
        else:
            return url + "?tag=" + AFFILIATE_TAG

    except:
        return url


# 🖼 Amazon image fetch
def get_amazon_image(url):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        html = requests.get(url, headers=headers, timeout=10).text

        patterns = [
            r'<meta property="og:image" content="([^"]+)"',
            r'"hiRes":"([^"]+)"',
            r'"large":"([^"]+)"'
        ]

        for p in patterns:
            match = re.search(p, html)
            if match:
                return match.group(1)

    except:
        return None

    return None


# 🤖 AUTO FORMAT FUNCTION
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


# 🤖 MAIN
def handle(update: Update, context: CallbackContext):
    msg = update.message
    text = msg.caption if msg.caption else msg.text

    if not text:
        return

    found_links = []

    def replace_link(match):
        link = match.group(0)

        if "amazon" in link or "amzn.to" in link:

            if "amzn.to" in link:
                link = expand_url(link)

            aff = make_affiliate(link)
            found_links.append(aff)
            return aff

        return link

    new_text = re.sub(r'https?://[^\s]+', replace_link, text)

    try:
        affiliate_link = found_links[0] if found_links else ""

        # 🔥 AUTO FORMAT
        final_post = format_post(new_text, affiliate_link)

        image_sent = False

        # ✅ image + caption same post
        if msg.photo:
            context.bot.send_photo(
                chat_id=CHANNEL_ID,
                photo=msg.photo[-1].file_id,
                caption=final_post,
                disable_web_page_preview=True
            )
            image_sent = True

        # ✅ Amazon image auto
        if not image_sent:
            for link in found_links:
                img = get_amazon_image(link)
                if img:
                    context.bot.send_photo(
                        chat_id=CHANNEL_ID,
                        photo=img,
                        caption=final_post,
                        disable_web_page_preview=True
                    )
                    image_sent = True
                    break

        # ✅ fallback text
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

    dp.add_handler(MessageHandler(Filters.all, handle))

    print("Bot Running 🚀")
    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
