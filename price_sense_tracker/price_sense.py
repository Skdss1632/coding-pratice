import time
import csv
import requests
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from webdriver_manager.firefox import GeckoDriverManager

# ---------------- TELEGRAM CONFIG ---------------- #
BOT_TOKEN = "7703865951:AAHrLXs2IzptdqBO0B6BJ4wSWrCZsZ-_V3Y"
CHAT_ID = "-1002460626267"   # Replace with your group chat ID

def send_telegram_message(message: str):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": message}
    requests.post(url, data=data)

# ---------------- PRICE TRACKER ---------------- #
def get_price_amazon(product_url: str):
    """Extract product name and price from Amazon"""
    options = Options()
    options.binary_location = "/usr/bin/firefox"
    service = Service(GeckoDriverManager().install())
    driver = webdriver.Firefox(service=service, options=Options())

    time.sleep(3)  # wait for page load

    try:
        product_name = driver.find_element(By.ID, "productTitle").text.strip()
    except:
        product_name = "Unknown Product"

    try:
        price_text = driver.find_element(By.CLASS_NAME, "a-price-whole").text
        price_text = price_text.replace(",", "").replace("₹", "").strip()
        current_price = int(price_text)
    except:
        current_price = None

    driver.quit()
    return product_name, current_price

# ---------------- MAIN LOGIC ---------------- #
def track_multiple_products(input_csv="products.csv", history_csv="price_history.csv"):
    df = pd.read_csv(input_csv)
    print(df)

    for index, row in df.iterrows():
        product_url = row['url']
        # print(product_url)
        target_price = int(row['target_price'])

        product_name, current_price = get_price_amazon(product_url)

        if current_price is None:
            print(f"❌ Failed to fetch price for {product_url}")
            continue

        print(f"🔎 {product_name} → Current Price: ₹{current_price}")

        # Save history in CSV
        with open(history_csv, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([time.strftime("%Y-%m-%d %H:%M:%S"), product_name, current_price, product_url])

        # Send alert if price drops
        if current_price <= target_price:
            msg = (
                f"🔥 Price Alert!\n\n"
                f"Product: {product_name}\n"
                f"Current Price: ₹{current_price}\n"
                f"Target Price: ₹{target_price}\n"
                f"Link: {product_url}"
            )
            send_telegram_message(msg)
            print("✅ Alert sent to Telegram group!")
        else:
            print("📉 No alert, price is still higher.")

# ---------------- RUN ---------------- #
if __name__ == "__main__":
    track_multiple_products()
