import time
import logging
import os
import asyncio
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from telegram import Bot

# Suppress TensorFlow logs (only errors will be shown)
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

# Suppress urllib3 warnings
logging.getLogger("urllib3").setLevel(logging.CRITICAL)

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger()

# Your Telegram Bot API token
API_TOKEN = '8154101977:AAFFUrg36NxCH9GcSx7xQoHmZ99TJpTqmEQ'  # Replace with your bot's API token
CHAT_ID = '5977807502'  # Replace with your chat ID (you can get this from a bot like @userinfobot)

# Create a bot instance directly without Request
bot = Bot(token=API_TOKEN)

# Function to send a message to Telegram asynchronously
async def send_telegram_message(message):
    try:
        await bot.send_message(chat_id=CHAT_ID, text=message, parse_mode="Markdown")
        logger.info("Message sent to Telegram.")
    except Exception as e:
        logger.error(f"Failed to send message: {e}")

# Function to get account details from environment variables
def get_account_details(account_index):
    account_prefix = f"ACCOUNT_{account_index}_"
    email = os.getenv(f"{account_prefix}EMAIL")
    password = os.getenv(f"{account_prefix}PASSWORD")
    server_name = os.getenv(f"{account_prefix}SERVER_NAME")

    if email and password and server_name:
        return {"email": email, "password": password, "server_name": server_name}
    else:
        logger.error(f"Missing details for account {account_index}")
        return None

# Function to extract item information
def item_information(driver, account_email, server_name):
    try:
        # Wait for the LOGIN COUNT element and extract the text (e.g., "LOGIN COUNT: 2 DAYS")
        login_count_text = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "/html/body/section/div/div/div[2]/h5"))
        ).text

        # Parse the login count (extract the number of days)
        login_days = int(login_count_text.split(":")[1].split()[0])

        # Build dynamic CSS selectors based on login_days
        claimed_day_selector = f"#xexchange > div:nth-child({login_days}) > div.reward-point"
        claimed_item_selector = f"#xexchange > div:nth-child({login_days}) > div.reward-name"

        # Extract the claimed day and item using the dynamic selectors
        claimed_day = driver.find_element(By.CSS_SELECTOR, claimed_day_selector).text
        claimed_item = driver.find_element(By.CSS_SELECTOR, claimed_item_selector).text

        # Construct the result message with improved Markdown formatting and aligned colons
        result_message = f"""
        *CLAIM DETAILS*

━━━━━━━━━━━━━━━━━━━━━━━━

➤ *Claimed   :* {claimed_day}
➤ *Item           :* {claimed_item}

━━━━━━━━━━━━━━━━━━━━━━━━

*Server     :* {server_name}
*Email       :* {account_email}
"""

        # Send the message asynchronously to Telegram
        loop = asyncio.get_event_loop()
        if loop.is_running():
            loop.create_task(send_telegram_message(result_message))
        else:
            loop.run_until_complete(send_telegram_message(result_message))

        logger.info(f"\n-----------------------------------")
        logger.info(f"Claimed on: {claimed_day}")
        logger.info(f"Item: {claimed_item}")
        logger.info(f"-----------------------------------")

    except Exception as e:
        logger.error(f"Error while extracting item information: {e}")

# Function to perform login and claim item for each account
def claim_item_for_account(account):
    try:
        logger.info(f"Starting automation for account: {account['email']}")

        options = webdriver.ChromeOptions()
        options.add_argument("--disable-notifications")
        options.add_argument("--disable-popup-blocking")
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        driver = webdriver.Chrome(options=options)

        driver.get("https://kageherostudio.com/event/?event=daily")
        time.sleep(5)

        login_button = driver.find_element(By.CLASS_NAME, "btn-login")
        login_button.click()

        time.sleep(5)

        email_field = driver.find_element(By.CSS_SELECTOR, "#form-login > fieldset > div:nth-child(1) > input")
        email_field.send_keys(account['email'])

        password_field = driver.find_element(By.CSS_SELECTOR, "#form-login > fieldset > div:nth-child(2) > input")
        password_field.send_keys(account['password'])

        login_submit_button = driver.find_element(By.CSS_SELECTOR, "#form-login > fieldset > div:nth-child(3) > button")
        login_submit_button.click()

        time.sleep(20)

        try:
            claim_button = driver.find_element(By.CSS_SELECTOR, "#xexchange > div.reward-content.dailyClaim.reward-star")
            if not claim_button.is_enabled():
                logger.info("Already Claimed! Claim back tomorrow!")
                item_information(driver, account['email'], account['server_name'])
                driver.quit()
                return
            claim_button.click()
            time.sleep(5)
            item_information(driver, account['email'], account['server_name'])

        except Exception as e:
            logger.info("Already Claimed! Claim back tomorrow!")
            item_information(driver, account['email'], account['server_name'])
            driver.quit()
            return

        server_select = driver.find_element(By.CSS_SELECTOR, "#form-server > fieldset > div:nth-child(1) > select")
        options = server_select.find_elements(By.TAG_NAME, "option")
        for option in options:
            if option.text == account['server_name']:
                option.click()
                break

        driver.find_element(By.CSS_SELECTOR, "#form-server-btnSubmit").click()
        alert = WebDriverWait(driver, 10).until(EC.alert_is_present())
        alert.accept()

        logger.info(f"Daily login task completed successfully for {account['email']}!")
        driver.quit()

    except Exception as e:
        logger.error(f"Error during automation: {e}")

# Run the automation for all accounts sequentially
def main():
    # Load accounts from GitHub secrets
    for i in range(1, 6):  # assuming you have 5 accounts, change this as needed
        account = get_account_details(i)
        if account:
            claim_item_for_account(account)
        else:
            logger.error(f"Skipping account {i} due to missing details")

if __name__ == "__main__":
    main()
