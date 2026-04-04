import requests
import time
from bs4 import BeautifulSoup
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

        data = {"long_url": url}

        res = requests.post(
            "https://api-ssl.bitly.com/v4/shorten",
            json=data,
            headers=headers,
            timeout=10
        )

        if res.status_code == 200:
            return res.json()["link"]
        else:
            return url

    except:
        return url


# 🟢 EarnKaro Deals Fetch
def get_deals():
    url = "https://earnkaro.com/store/flipkart"
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        res = requests.get(url, headers=headers, timeout=10)
    except:
        print("Deal site error")
        return []

    soup = BeautifulSoup(res.text, "html.parser")

    deals = []

    for a in soup.find_all("a", href=True):
        link = a["href"]

        # Only Flipkart links
        if "flipkart" in link.lower():
            deals.append(("🔥 Flipkart Deal", "", "", link))

    return deals


# 📢 Telegram Post
def post_to_telegram(deals):
    for title, price, old_price, link in deals:

        if link in posted_links:
            continue

        short_link = shorten_bitly(link)

        msg = f"""{title}

👉 Buy Now: {short_link}
"""

        try:
            bot.send_message(chat_id=CHANNEL_ID, text=msg)
            posted_links.add(link)
            print("Posted:", link)
            time.sleep(2)

        except Exception as e:
            print("Telegram Error:", e)


# 🔁 MAIN LOOP
while True:
    try:
        deals = get_deals()

        if deals:
            post_to_telegram(deals)

        print("Checked for new deals...")
        time.sleep(1800)  # 30 min

    except Exception as e:
        print("Error:", e)
        time.sleep(60)
