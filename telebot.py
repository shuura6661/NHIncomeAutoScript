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
API_TOKEN = ''  # Replace with your bot's API token
CHAT_ID = ''  # Replace with your chat ID (you can get this from a bot like @userinfobot)

# Create a bot instance directly without Request
bot = Bot(token=API_TOKEN)

# List of account credentials (email and password) along with server names
accounts = [
    {"email": "@gmail.com", "password": "", "server_name": ""},
    {"email": "@gmail.com", "password": "!", "server_name": ""}
]

# Function to send a message to Telegram asynchronously
async def send_telegram_message(message):
    try:
        await bot.send_message(chat_id=CHAT_ID, text=message, parse_mode="Markdown")
        logger.info("Message sent to Telegram.")
    except Exception as e:
        logger.error(f"Failed to send message: {e}")

# Function to extract and log the item and day details after a successful claim or failure
def itemInformation(driver, account_email, server_name):
    try:
        # Wait for the claimed item and day to be visible (adjust CSS selector if necessary)
        claimed_day = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#xexchange > div.reward-content.dailyClaim.grayscale > div.reward-point"))
        ).text
        
        claimed_item = driver.find_element(By.CSS_SELECTOR, "#xexchange > div.reward-content.dailyClaim.grayscale > div.reward-name").text

        # Construct the result message with Markdown formatting
        result_message = f"""
*Claimed Details:*

*Claimed On:* {claimed_day}
*Item:* {claimed_item}

- - -

*Email:* {account_email}
*Server:* {server_name}
        """

        # Get the current event loop for the current thread, or create a new one if it doesn't exist
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # If a loop is already running (in case of multiple threads), use a background task
            loop.create_task(send_telegram_message(result_message))
        else:
            # If no loop is running, create a new one
            loop.run_until_complete(send_telegram_message(result_message))

        # Log the details with colors in the console
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

        # Set up the Chrome WebDriver with specific options (headless mode, notifications off, etc.)
        options = webdriver.ChromeOptions()
        options.add_argument("--disable-notifications")
        options.add_argument("--disable-popup-blocking")
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        driver = webdriver.Chrome(options=options)

        # Open the website for the daily event
        driver.get("https://kageherostudio.com/event/?event=daily")
        time.sleep(5)  # Wait for the page to load

        # Click the LOGIN button...
        logger.info("Clicking the LOGIN button...")
        login_button = driver.find_element(By.CLASS_NAME, "btn-login")
        login_button.click()

        time.sleep(5)  # Wait for login modal

        # Fill in login credentials and submit
        logger.info(f"Entering email: {account['email']}")
        email_field = driver.find_element(By.CSS_SELECTOR, "#form-login > fieldset > div:nth-child(1) > input")
        email_field.send_keys(account['email'])

        logger.info(f"Entering password for {account['email']}")
        password_field = driver.find_element(By.CSS_SELECTOR, "#form-login > fieldset > div:nth-child(2) > input")
        password_field.send_keys(account['password'])

        login_submit_button = driver.find_element(By.CSS_SELECTOR, "#form-login > fieldset > div:nth-child(3) > button")
        login_submit_button.click()

        time.sleep(5)  # Wait for the main page to load

        # Extract the item and day details after the claim
        itemInformation(driver, account['email'], account['server_name'])

        driver.quit()  # Close the browser after completing the task

    except Exception as e:
        logger.error(f"Error during automation: {e}")


# Run the automation for all accounts sequentially (one by one)
def main():
    for account in accounts:
        claim_item_for_account(account)

if __name__ == "__main__":
    main()
