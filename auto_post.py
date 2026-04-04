import re
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, MessageHandler, Filters, CallbackContext

BOT_TOKEN = "8645119625:AAEnBkJ5ND1z06BS9ui4YX_nkFJ8kwLgFY0"
CHANNEL_ID = -1002161382456
BITLY_TOKEN = "e3df1684c678e66ab90b1a3746f57852e4b3eff0"
AFFILIATE_TAG = "partha07e-21"

posted = set()

def shorten(url):
try:
headers = {
"Authorization": f"Bearer {BITLY_TOKEN}",
"Content-Type": "application/json"
}
r = requests.post(
"https://api-ssl.bitly.com/v4/shorten",
json={"long_url": url},
headers=headers
)
if r.status_code == 200:
return r.json()["link"]
except:
pass
return url

def expand(url):
try:
return requests.get(url, allow_redirects=True).url
except:
return url

def amazon_aff(url):
if "amazon." in url:
return url.split("?")[0] + "?tag=" + AFFILIATE_TAG
return url

def handle(update: Update, context: CallbackContext):
msg = update.message
text = msg.text or msg.caption or ""

```
if not text:
    return

match = re.search(r'https?://\S+', text)
if not match:
    return

link = match.group(0)

link = expand(link)
link = amazon_aff(link)

if link in posted:
    return
posted.add(link)

short = shorten(link)

caption = f"""🔥 DEAL ALERT 🔥
```

💥 Grab Now 💥

👉 BUY NOW 👇
{short}

⚡ Limited Time Deal"""

```
button = InlineKeyboardMarkup([
    [InlineKeyboardButton("🔥 Buy Now", url=short)]
])

if msg.photo:
    context.bot.send_photo(
        chat_id=CHANNEL_ID,
        photo=msg.photo[-1].file_id,
        caption=caption,
        reply_markup=button
    )
else:
    context.bot.send_message(
        chat_id=CHANNEL_ID,
        text=caption,
        reply_markup=button,
        disable_web_page_preview=True
    )
```

def main():
updater = Updater(BOT_TOKEN, use_context=True)
updater.bot.delete_webhook(drop_pending_updates=True)

```
dp = updater.dispatcher
dp.add_handler(MessageHandler(Filters.text | Filters.photo, handle))

updater.start_polling()
updater.idle()
```

if **name** == "**main**":
main()
