import requests
import time
import random
from bs4 import BeautifulSoup
from telegram import Bot

# 🔑 CONFIG
BOT_TOKEN = "8645119625:AAEnBkJ5ND1z06BS9ui4YX_nkFJ8kwLgFY0"
CHANNEL_ID = -1002161382456   # private hole -100xxxx
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


# 🟢 Deal Fetch (Improved Filter)
def get_deals():
    url = "https://earnkaro.com/store/flipkart"
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        res = requests.get(url, headers=headers, timeout=10)
    except:
        print("❌ Fetch failed")
        return []

    soup = BeautifulSoup(res.text, "html.parser")

    links = []

    for a in soup.find_all("a", href=True):
        link = a["href"]

        # only valid external product-like links
        if link.startswith("http") and not any(x in link for x in [
            "earnkaro", "facebook", "twitter", "instagram", "youtube"
        ]):
            links.append(link)

    # remove duplicate
    links = list(set(links))

    print(f"✅ Found {len(links)} links")

    return links[:8]   # limit


# 📢 Telegram Post (Better format)
def post_to_telegram(links):
    for link in links:

        if link in posted_links:
            continue

        short_link = shorten_bitly(link)

        msg = f"""🔥 HOT DEAL ALERT 🔥

🛍 Limited Time Offer
💸 Grab Now Before Price Increases!

👉 {short_link}

#flipkart #deals #shopping
"""

        try:
            bot.send_message(chat_id=CHANNEL_ID, text=msg)
            posted_links.add(link)

            print("✅ Posted:", short_link)

            time.sleep(random.randint(2,5))  # safe delay

        except Exception as e:
            print("❌ Telegram Error:", e)


# 🚀 START
print("🚀 PRO BOT STARTED...")

while True:
    try:
        deals = get_deals()

        if deals:
            post_to_telegram(deals)
        else:
            print("⚠️ No deals found")

        print("⏳ Waiting next cycle...\n")
        time.sleep(1800)

    except Exception as e:
        print("❌ Error:", e)
        time.sleep(60)
