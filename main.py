import os
import time
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

DAILY_URL = "https://kageherostudio.com/event/?event=daily"


def load_accounts():
    """EMAIL1/PASSWORD1/SERVER_NAME1, EMAIL2/... from env (GitHub Secrets-friendly)."""
    accounts, i = [], 1
    while os.getenv(f"EMAIL{i}"):
        email = os.getenv(f"EMAIL{i}")
        pw = os.getenv(f"PASSWORD{i}")
        srv = os.getenv(f"SERVER_NAME{i}")
        if pw and srv:
            accounts.append({"email": email, "password": pw, "server_name": srv})
        i += 1
    return accounts


def build_driver():
    o = webdriver.ChromeOptions()
    o.add_argument("--headless=new")
    o.add_argument("--disable-gpu")
    o.add_argument("--no-sandbox")
    o.add_argument("--disable-dev-shm-usage")
    o.add_argument("--disable-notifications")
    o.add_argument("--window-size=1366,900")
    return webdriver.Chrome(options=o)  # Selenium 4.8 auto-manages the driver


def login(driver, wait, email, password):
    driver.get(DAILY_URL)
    wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".btn-login"))).click()
    wait.until(EC.visibility_of_element_located(
        (By.CSS_SELECTOR, 'input[name="txtuserid"]'))).send_keys(email)
    driver.find_element(By.CSS_SELECTOR, 'input[name="txtpassword"]').send_keys(password)
    driver.find_element(By.CSS_SELECTOR, "#form-login-btnSubmit").click()
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#xexchange .dailyClaim")))


def claim(driver, wait, server_name):
    cards = driver.find_elements(
        By.CSS_SELECTOR, "#xexchange .dailyClaim.reward-star:not(.grayscale)")
    if not cards:
        logger.warning("No claimable reward (already claimed/locked). Back tomorrow.")
        return False

    card = cards[0]
    item = card.get_attribute("data-name")
    logger.info(f"Claimable item: {item}")

    # Site fires a native confirm() before the final claim AJAX -> auto-accept it
    driver.execute_script("window.confirm = function(){ return true; };")
    card.click()  # opens #ServerForm modal

    select_el = wait.until(EC.visibility_of_element_located(
        (By.CSS_SELECTOR, 'select[name="selserver"]')))
    sel = Select(select_el)
    if not any(o.text.strip() == server_name.strip() for o in sel.options):
        logger.error(f"Server '{server_name}' not found. "
                     f"Available: {[o.text.strip() for o in sel.options]}")
        return False
    sel.select_by_visible_text(server_name.strip())

    driver.find_element(By.CSS_SELECTOR, "#form-server-btnSubmit").click()
    time.sleep(5)  # AJAX act=daily -> success + reload
    logger.info(f"Claim submitted: '{item}' on '{server_name}'.")
    return True


def main():
    accounts = load_accounts()
    if not accounts:
        logger.error("No accounts. Set EMAIL1/PASSWORD1/SERVER_NAME1 env vars.")
        return
    for acc in accounts:
        driver = build_driver()
        wait = WebDriverWait(driver, 25)
        try:
            logger.info(f"Processing {acc['email']}")
            login(driver, wait, acc["email"], acc["password"])
            claim(driver, wait, acc["server_name"])
        except TimeoutException as e:
            logger.error(f"Timeout for {acc['email']}: {e}")
        except Exception as e:
            logger.error(f"Error for {acc['email']}: {e}")
        finally:
            driver.quit()


if __name__ == "__main__":
    main()
