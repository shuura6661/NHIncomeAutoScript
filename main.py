from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import logging
import os
from termcolor import colored  # For adding color to console output

# Suppress TensorFlow logs to reduce clutter (only errors will be shown)
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

# Suppress urllib3 warnings (they're not critical for this script)
logging.getLogger("urllib3").setLevel(logging.CRITICAL)

# Configure logging to include timestamps and log levels for better traceability
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger()

# List of account credentials (email and password) along with server names
accounts = [
    {"email": "@gmail.com", "password": "", "server_name": ""},
    {"email": "@gmail.com", "password": "!", "server_name": ""}
]

# Function to extract and log the item and day details after a successful claim or failure
def itemInformation():
    try:
        # Attempt to locate the elements for claimed item and day on the page (adjust CSS selectors as needed)
        claimed_day = driver.find_element(By.CSS_SELECTOR, "#xexchange > div.reward-content.dailyClaim.grayscale > div.reward-point").text
        claimed_item = driver.find_element(By.CSS_SELECTOR, "#xexchange > div.reward-content.dailyClaim.grayscale > div.reward-name").text

        # Log the extracted details in a colorful and clear format
        logger.info(colored(f"\n-----------------------------------", "cyan"))
        logger.info(colored(f"Claimed on: {claimed_day}", "yellow"))
        logger.info(colored(f"Item: {claimed_item}", "green"))
        logger.info(colored(f"-----------------------------------", "cyan"))

    except Exception as e:
        # Log any errors that occur while extracting the item details
        logger.error(colored(f"Error while extracting item information: {e}", "red"))

# Loop through the list of accounts and process each one
for account in accounts:
    try:
        # Start a new browser session for each account and log the start
        logger.info(colored(f"\nStarting automation for account: {account['email']}", "magenta"))

        # Set up the Chrome WebDriver with specific options (headless mode, notifications off, etc.)
        options = webdriver.ChromeOptions()
        options.add_argument("--disable-notifications")  # Disable browser notifications
        options.add_argument("--disable-popup-blocking")  # Disable popups
        options.add_argument("--headless")  # Run in headless mode to avoid GUI
        options.add_argument("--disable-gpu")  # Necessary for headless mode on certain systems
        driver = webdriver.Chrome(options=options)

        # Step 1: Open the website for the daily event
        driver.get("https://kageherostudio.com/event/?event=daily")
        time.sleep(5)  # Wait for the page to load

        # Step 2: Click the login button on the page
        logger.info(colored("Clicking the LOGIN button...", "blue"))
        login_button = driver.find_element(By.CLASS_NAME, "btn-login")
        login_button.click()

        # Step 3: Wait for the login modal to appear
        time.sleep(5)

        # Step 4: Fill in the login credentials (email and password)
        logger.info(f"Entering email: {account['email']}.")
        email_field = driver.find_element(By.CSS_SELECTOR, "#form-login > fieldset > div:nth-child(1) > input")
        email_field.send_keys(account['email'])

        logger.info(f"Entering password for {account['email']}.")
        password_field = driver.find_element(By.CSS_SELECTOR, "#form-login > fieldset > div:nth-child(2) > input")
        password_field.send_keys(account['password'])

        # Step 5: Submit the login form to authenticate
        logger.info(colored("Submitting the Login Form...", "blue"))
        submit_button = driver.find_element(By.CSS_SELECTOR, "#form-login-btnSubmit")
        submit_button.click()

        logger.info("Waiting 20 seconds for the page to load after login.")
        time.sleep(20)

        # Step 6: Attempt to claim the daily item (button click)
        try:
            logger.info("Attempting to claim the item...")
            claim_button = driver.find_element(By.CSS_SELECTOR, "#xexchange > div.reward-content.dailyClaim.reward-star")

            # Check if the button is enabled or already disabled (item already claimed)
            if not claim_button.is_enabled():  # Button is disabled if already claimed
                logger.warning(colored("Already claimed! Claim back tomorrow.", "yellow"))
                itemInformation()  # Log the item information in case of already claimed
                driver.quit()  # Close the browser session early
                continue  # Skip to the next account

            # If the button is enabled, click to claim the item
            claim_button.click()
            logger.info("Waiting 5 seconds to load the claim result...")
            time.sleep(5)

            # Call itemInformation after successfully claiming the item
            itemInformation()

        except Exception as e:
            # Log warning if there's an error (item already claimed or another issue)
            logger.warning(colored("Already claimed or an error occurred.", "yellow"))
            itemInformation()  # Log item details even on failure

        finally:
            # Ensure the browser session is closed after processing each account
            driver.quit()

    except Exception as e:
        # Log any errors that occur while processing the account
        logger.error(colored(f"Error processing account {account['email']}: {e}", "red"))
