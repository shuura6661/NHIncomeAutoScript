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

def item_information(driver, account_email, server_name):
    try:
        # Wait for the LOGIN COUNT element and extract the text (e.g., "LOGIN COUNT: 2 DAYS")
        login_count_text = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "/html/body/section/div/div/div[2]/h5"))
        ).text

        # Parse the login count (extract the number of days)
        login_days = int(login_count_text.split(":")[1].split()[0])

        # Build dynamic CSS selectors based on login_days
        # For example: day 1 -> nth-child(1), day 2 -> nth-child(2), ..., day 31 -> nth-child(31)
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
➤ *Item          :* {claimed_item}

━━━━━━━━━━━━━━━━━━━━━━━━

*Server     :* {server_name}
*Email       :* {account_email}
"""


        # Send the message asynchronously to Telegram
        loop = asyncio.get_event_loop()
        if loop.is_running():
            loop.create_task(send_telegram_message(result_message))  # Use background task if loop is running
        else:
            loop.run_until_complete(send_telegram_message(result_message))  # Run if no loop exists

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

        time.sleep(20)

        # Try to click the item icon (Claim button)
        try:
            logger.info("Attempting to click active item.")
            claim_button = driver.find_element(By.CSS_SELECTOR, "#xexchange > div.reward-content.dailyClaim.reward-star")

            # If the button is disabled, it means the item has already been claimed
            if not claim_button.is_enabled():
                logger.info("Already Claimed! Claim back tomorrow!")
                item_information(driver, account['email'], account['server_name'])  # Pass both email and server_name
                driver.quit()  # Exit early if already claimed
                return  # Skip to the next account

            # If the button is enabled, proceed with claiming
            claim_button.click()
            logger.info("Waiting 5 seconds to load.")
            time.sleep(5)

            # Call itemInformation after successfully claiming the item
            item_information(driver, account['email'], account['server_name'])  # Pass both email and server_name

        except Exception as e:
            # Only log the "Already Claimed!" message, suppress the actual error
            logger.info("Already Claimed! Claim back tomorrow!")
            item_information(driver, account['email'], account['server_name'])  # Pass both email and server_name
            driver.quit()  # Exit early if the item can't be claimed
            return  # Skip to the next account


        # Choose server - custom server selection by server name
        logger.info(f"Choosing server for account {account['email']}.")

        server_name = account['server_name']  # Get the server name for this account

        # Find the select dropdown element
        server_select = driver.find_element(By.CSS_SELECTOR, "#form-server > fieldset > div:nth-child(1) > select")
        
        # Find all option elements in the select dropdown
        options = server_select.find_elements(By.TAG_NAME, "option")

        # Loop through each option and select the one that matches the server name
        for option in options:
            if option.text == server_name or option.get_attribute("data-server") == server_name:
                logger.info(f"Selecting {server_name}.")
                option.click()
                break

        # Click Submit
        driver.find_element(By.CSS_SELECTOR, "#form-server-btnSubmit").click()

        # Handle the browser pop-up alert (OK/Cancel)
        alert = WebDriverWait(driver, 10).until(EC.alert_is_present())
        alert.accept()  # Accept the alert (Click OK)

        logger.info(f"Daily login task completed successfully for {account['email']}!")

        # Extract the item and day details after the claim
        item_information(driver, account['email'])

        driver.quit()  # Close the browser after completing the task

    except Exception as e:
        logger.error(f"Error during automation: {e}")

# Run the automation for all accounts sequentially (one by one)
def main():
    for account in accounts:
        claim_item_for_account(account)

if __name__ == "__main__":
    main()
