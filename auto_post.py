import re
import asyncio
from telegram import Bot
from telegram.ext import Updater, MessageHandler, Filters
from playwright.async_api import async_playwright

BOT_TOKEN = "8770723867:AAHUi2zo7O-I4nF-uLl_1i0Cy6_aj9dWH_I"
CHANNEL = -1002161382456
AFFILIATE_TAG = "partha07e-21"

bot = Bot(token=BOT_TOKEN)

# 🔥 Affiliate link add
def add_tag(url):
    if "amazon" in url:
        if "?" in url:
            return url + "&tag=" + AFFILIATE_TAG
        else:
            return url + "?tag=" + AFFILIATE_TAG
    return url

# 🔥 Screenshot function
async def take_screenshot(url):
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(viewport={"width": 1080, "height": 1920})

        await page.goto(url)
        await page.wait_for_timeout(6000)

        # 🔥 product section crop
        element = await page.query_selector("#centerCol")

        path = "product.png"

        if element:
            await element.screenshot(path=path)
        else:
            await page.screenshot(path=path)

        await browser.close()
        return path

# 🔥 Main handler
def handle(update, context):
    text = update.message.text
    links = re.findall(r'https?://\S+', text)

    if not links:
        return

    url = links[0]
    aff_link = add_tag(url)

    # 🔥 screenshot
    path = asyncio.run(take_screenshot(url))

    caption = f"🛒 Buy Now:\n{aff_link}"

    try:
        bot.send_photo(
            chat_id=CHANNEL,
            photo=open(path, "rb"),
            caption=caption
        )

        update.message.reply_text("✅ Screenshot Posted!")

    except Exception as e:
        update.message.reply_text(f"❌ Error: {e}")

# 🚀 Run bot
updater = Updater(BOT_TOKEN, use_context=True)
dp = updater.dispatcher
dp.add_handler(MessageHandler(Filters.text, handle))

print("Bot Running 🚀")
updater.start_polling()
updater.idle()
