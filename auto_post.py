import requests
import time
import re
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
            headers=headers
        )

        if res.status_code == 200:
            return res.json()["link"]
        else:
            return url

    except:
        return url


# 🛒 Flipkart Deals Fetch
def get_flipkart_deals():
    url = "https://www.flipkart.com/offers-store"
    headers = {"User-Agent": "Mozilla/5.0"}

    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    deals = []

    for item in soup.select("a._1fQZEK"):
        try:
            link = "https://www.flipkart.com" + item.get("href")

            title_tag = item.select_one("._4rR01T")
            price_tag = item.select_one("._30jeq3")
            old_price_tag = item.select_one("._3I9_wc")

            title = title_tag.text if title_tag else "Product"
            price = price_tag.text if price_tag else ""
            old_price = old_price_tag.text if old_price_tag else ""

            deals.append((title, price, old_price, link))

        except:
            continue

    return deals


# 📢 Telegram Post
def post_to_telegram(deals):
    for title, price, old_price, link in deals:

        if link in posted_links:
            continue

        short_link = shorten_bitly(link)

        msg = f"""🔥 Flipkart Deal

🛍 {title}
💰 {price} ~~{old_price}~~

👉 Buy Now: {short_link}
"""

        try:
            bot.send_message(chat_id=CHANNEL_ID, text=msg)
            posted_links.add(link)
            print("Posted:", title)
            time.sleep(2)

        except Exception as e:
            print("Telegram Error:", e)


# 🔁 MAIN LOOP
while True:
    try:
        deals = get_flipkart_deals()

        if deals:
            post_to_telegram(deals)

        print("Checked for new deals...")
        time.sleep(1800)  # 30 min

    except Exception as e:
        print("Error:", e)
        time.sleep(60)
