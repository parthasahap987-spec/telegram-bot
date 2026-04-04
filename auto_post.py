import requests
import time
import random
import re
from telegram import Bot

# 🔑 CONFIG
BOT_TOKEN = "8645119625:AAEnBkJ5ND1z06BS9ui4YX_nkFJ8kwLgFY0"
CHANNEL_ID = -1002161382456
BITLY_TOKEN = "e3df1684c678e66ab90b1a3746f57852e4b3eff0"

bot = Bot(token=BOT_TOKEN)

posted_links = set()

# 🔗 Bitly Shortener
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
        else:
            return url

    except:
        return url


# 🟢 DEAL FETCH (NO XML ERROR)
def get_deals():
    url = "https://rss.app/feeds/_bJ7ZPz0sQZ6g6x0M.xml"

    try:
        res = requests.get(url, timeout=10)
        text = res.text
    except:
        print("❌ Fetch failed")
        return []

    # extract all links using regex
    links = re.findall(r"<link>(.*?)</link>", text)

    clean_links = []

    for link in links:
        if link.startswith("http") and link not in posted_links:
            clean_links.append(link)

    print("✅ Deals found:", len(clean_links))

    return clean_links[:5]


# 📢 Telegram Post
def post_to_telegram(links):
    for link in links:

        short_link = shorten_bitly(link)

        msg = f"""🔥 HOT DEAL

👉 Buy Now: {short_link}
"""

        try:
            bot.send_message(chat_id=CHANNEL_ID, text=msg)
            posted_links.add(link)

            print("✅ Posted:", short_link)

            time.sleep(random.randint(2,5))

        except Exception as e:
            print("❌ Telegram Error:", e)


# 🚀 START
print("🚀 BOT STARTED (FINAL FIX)")

while True:
    try:
        deals = get_deals()

        if deals:
            post_to_telegram(deals)
        else:
            print("⚠️ No deals")

        print("⏳ Waiting...\n")
        time.sleep(1800)

    except Exception as e:
        print("❌ Error:", e)
        time.sleep(60)
