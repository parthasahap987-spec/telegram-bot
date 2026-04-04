import re
import requests
import io
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, MessageHandler, Filters, CallbackContext

# 🔑 CONFIG

BOT_TOKEN = "8645119625:AAEnBkJ5ND1z06BS9ui4YX_nkFJ8kwLgFY0"
CHANNELS = [-1002161382456]
AFFILIATE_TAG = "partha07e-21"
BITLY_TOKEN = "e3df1684c678e66ab90b1a3746f57852e4b3eff0"

posted_links = set()

# 🔗 Bitly Short Link

def shorten_bitly(url):
try:
headers = {
"Authorization": f"Bearer {BITLY_TOKEN}",
"Content-Type": "application/json"
}

```
    res = requests.post(
        "https://api-ssl.bitly.com/v4/shorten",
        json={"long_url": url},
        headers=headers,
        timeout=10
    )

    if res.status_code == 200:
        return res.json()["link"]
    else:
        print("Bitly Error:", res.text)
        return None

except Exception as e:
    print("Bitly Exception:", e)
    return None
```

# 🔁 Backup Short Link (TinyURL)

def shorten_backup(url):
try:
res = requests.get(f"http://tinyurl.com/api-create.php?url={url}", timeout=10)
return res.text
except:
return url

# 🔗 Final Shortener

def shorten_link(url):
short = shorten_bitly(url)
if short:
return short
return shorten_backup(url)

# 🔁 Expand short links (ALL links)

def expand_url(url):
try:
session = requests.Session()
session.headers.update({"User-Agent": "Mozilla/5.0"})
res = session.get(url, allow_redirects=True, timeout=10)
return res.url
except:
return url

# 🔗 Amazon affiliate

def make_amazon_affiliate(url):
try:
match = re.search(r'(https://www\.amazon\.[^/]+/dp/[A-Z0-9]+)', url)
if match:
clean = match.group(1)
else:
clean = url.split("?")[0]

```
    return clean + "?tag=" + AFFILIATE_TAG
except:
    return url
```

# 🖼 Amazon image

def get_amazon_image(url):
try:
headers = {
"User-Agent": "Mozilla/5.0",
"Accept-Language": "en-US,en;q=0.9"
}

```
    html = requests.get(url, headers=headers, timeout=10).text

    patterns = [
        r'<meta property="og:image" content="([^"]+)"',
        r'"hiRes":"([^"]+)"'
    ]

    for p in patterns:
        match = re.search(p, html)
        if match:
            img = match.group(1).replace("\\", "")
            if img.startswith("http"):
                return img
except:
    pass

return None
```

# 📸 send image

def send_image(bot, chat_id, img_url, caption, button):
try:
res = requests.get(img_url, stream=True, timeout=10)
if res.status_code == 200:
img = io.BytesIO(res.content)
img.name = "product.jpg"

```
        bot.send_photo(
            chat_id=chat_id,
            photo=img,
            caption=caption,
            reply_markup=button
        )
        return True
except:
    return False
return False
```

# 🧾 format

def format_post(text, link):
return f"""🔥 DEAL ALERT 🔥

💥 Grab Now 💥

🛒 {text.splitlines()[0]}

👉 BUY NOW 👇
{link}

⚡ Limited Time Deal"""

# 🤖 MAIN

def handle(update: Update, context: CallbackContext):
msg = update.message
text = msg.caption if msg.caption else msg.text if msg.text else ""

```
if not text.strip():
    return

found_link = ""

def replace_link(match):
    nonlocal found_link
    link = match.group(0)

    # 🔓 Expand ALL short links (bit.ly, amzn, etc.)
    link = expand_url(link)

    # 🛒 Amazon হলে affiliate add
    if "amazon." in link:
        link = make_amazon_affiliate(link)

    # ✅ ANY link accept (Flipkart, Meesho, Myntra, etc.)
    found_link = link
    return link

new_text = re.sub(r'https?://[^\s]+', replace_link, text)

if not found_link:
    return

# ❌ duplicate block
if found_link in posted_links:
    return
posted_links.add(found_link)

# 🔗 short link
short_link = shorten_link(found_link)

# 🔘 button
button = InlineKeyboardMarkup([
    [InlineKeyboardButton("🔥 Buy Now", url=short_link)]
])

final_post = format_post(new_text, short_link)

# 📤 send
for ch in CHANNELS:

    image_sent = False

    if msg.photo:
        context.bot.send_photo(
            chat_id=ch,
            photo=msg.photo[-1].file_id,
            caption=final_post,
            reply_markup=button
        )
        image_sent = True

    if not image_sent and "amazon." in found_link:
        img = get_amazon_image(found_link)
        if img:
            if send_image(context.bot, ch, img, final_post, button):
                image_sent = True

    if not image_sent:
        context.bot.send_message(
            chat_id=ch,
            text=final_post,
            reply_markup=button,
            disable_web_page_preview=True
        )
```

# 🚀 RUN

def main():
updater = Updater(BOT_TOKEN, use_context=True)

```
updater.bot.delete_webhook(drop_pending_updates=True)

dp = updater.dispatcher

dp.add_handler(MessageHandler(
    Filters.text | Filters.caption | Filters.photo,
    handle
))

print("🔥 Bot Running (ALL LINKS + Bitly)...")
updater.start_polling()
updater.idle()
```

if **name** == "**main**":
main()
