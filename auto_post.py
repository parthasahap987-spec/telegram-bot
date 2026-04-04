import re
import requests
import io
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, MessageHandler, Filters, CallbackContext

BOT_TOKEN = "8645119625:AAEnBkJ5ND1z06BS9ui4YX_nkFJ8kwLgFY0"
CHANNELS = [-1002161382456]
AFFILIATE_TAG = "partha07e-21"
BITLY_TOKEN = "e3df1684c678e66ab90b1a3746f57852e4b3eff0"

posted_links = set()

def shorten_bitly(url):
try:
headers = {
"Authorization": f"Bearer {BITLY_TOKEN}",
"Content-Type": "application/json"
}
res = requests.post(
"https://api-ssl.bitly.com/v4/shorten",
json={"long_url": url},
headers=headers,
timeout=10
)
if res.status_code == 200:
return res.json()["link"]
return None
except:
return None

def shorten_backup(url):
try:
return requests.get(f"http://tinyurl.com/api-create.php?url={url}").text
except:
return url

def shorten_link(url):
short = shorten_bitly(url)
return short if short else shorten_backup(url)

def expand_url(url):
try:
return requests.get(url, allow_redirects=True, timeout=10).url
except:
return url

def make_amazon_affiliate(url):
try:
return url.split("?")[0] + "?tag=" + AFFILIATE_TAG
except:
return url

def format_post(text, link):
return f"""🔥 DEAL ALERT 🔥

💥 Grab Now 💥

🛒 {text.splitlines()[0]}

👉 BUY NOW 👇
{link}

⚡ Limited Time Deal"""

def handle(update: Update, context: CallbackContext):
msg = update.message
text = msg.text or msg.caption or ""

```
if not text:
    return

found_link = ""

def replace_link(match):
    nonlocal found_link
    link = expand_url(match.group(0))

    if "amazon." in link:
        link = make_amazon_affiliate(link)

    found_link = link
    return link

re.sub(r'https?://\S+', replace_link, text)

if not found_link:
    return

if found_link in posted_links:
    return
posted_links.add(found_link)

short_link = shorten_link(found_link)

button = InlineKeyboardMarkup([
    [InlineKeyboardButton("🔥 Buy Now", url=short_link)]
])

final_post = format_post(text, short_link)

for ch in CHANNELS:
    if msg.photo:
        context.bot.send_photo(
            chat_id=ch,
            photo=msg.photo[-1].file_id,
            caption=final_post,
            reply_markup=button
        )
    else:
        context.bot.send_message(
            chat_id=ch,
            text=final_post,
            reply_markup=button,
            disable_web_page_preview=True
        )
```

def main():
updater = Updater(BOT_TOKEN, use_context=True)

```
updater.bot.delete_webhook(drop_pending_updates=True)

dp = updater.dispatcher
dp.add_handler(MessageHandler(Filters.text | Filters.photo | Filters.caption, handle))

updater.start_polling()
updater.idle()
```

if **name** == "**main**":
main()
