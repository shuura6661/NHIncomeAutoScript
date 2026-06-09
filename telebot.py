import os
import time
import logging
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

DAILY_URL = "https://kageherostudio.com/event/?event=daily"

# Telegram config from env (GitHub Secrets friendly) -- never hardcode tokens
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")


def send_telegram_message(message: str) -> None:
    """Fire-and-forget Telegram notify via HTTP API (sync, no event loop)."""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        logger.warning("Telegram token/chat_id not set; skipping notification.")
        return
    try:
        resp = requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
            data={"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "Markdown"},
            timeout=15,
        )
        if resp.status_code == 200:
            logger.info("Telegram notification sent.")
        else:
            logger.error(f"Telegram send failed [{resp.status_code}]: {resp.text[:200]}")
    except Exception as e:
        logger.error(f"Telegram send error: {e}")


def load_accounts():
    """Auto-detect EMAIL1/PASSWORD1/SERVER_NAME1, EMAIL2/... from env."""
    accounts, i = [], 1
    while os.getenv(f"EMAIL{i}"):
        pw = os.getenv(f"PASSWORD{i}")
        srv = os.getenv(f"SERVER_NAME{i}")
        if pw and srv:
            accounts.append({
                "email": os.getenv(f"EMAIL{i}"),
                "password": pw,
                "server_name": srv,
            })
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
    return webdriver.Chrome(options=o)  # Selenium 4.8 auto-manages chromedriver


def login(driver, wait, email, password):
    driver.get(DAILY_URL)
    wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".btn-login"))).click()
    wait.until(EC.visibility_of_element_located(
        (By.CSS_SELECTOR, 'input[name="txtuserid"]'))).send_keys(email)
    driver.find_element(By.CSS_SELECTOR, 'input[name="txtpassword"]').send_keys(password)
    driver.find_element(By.CSS_SELECTOR, "#form-login-btnSubmit").click()
    # Wait for the AUTHENTICATED state. The reward grid exists even when logged
    # out, so keying off it returns instantly and races ahead of the login modal
    # (the backdrop then intercepts reward clicks -> "element not interactable").
    # The site shows a "Logout" link only once authenticated; also wait for the
    # modal backdrop to clear so reward cards become interactable.
    wait.until(lambda d: "logout" in d.find_element(By.TAG_NAME, "body").text.lower())
    wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, ".modal-backdrop")))


def claim(driver, wait, server_name):
    cards = driver.find_elements(
        By.CSS_SELECTOR, "#xexchange .dailyClaim.reward-star:not(.grayscale)")
    if not cards:
        return {"status": "already_claimed", "item": None}

    card = cards[0]
    item = card.get_attribute("data-name")

    # Site shows a native confirm() before the final claim AJAX -- auto-accept it
    driver.execute_script("window.confirm = function(){ return true; };")
    card.click()  # opens the #ServerForm modal

    select_el = wait.until(EC.visibility_of_element_located(
        (By.CSS_SELECTOR, 'select[name="selserver"]')))
    sel = Select(select_el)
    available = [o.text.strip() for o in sel.options]
    if server_name.strip() not in available:
        return {"status": "server_not_found", "item": item, "available": available}
    sel.select_by_visible_text(server_name.strip())

    driver.find_element(By.CSS_SELECTOR, "#form-server-btnSubmit").click()
    time.sleep(5)  # AJAX act=daily -> success + page reload
    return {"status": "claimed", "item": item}


def notify(acc, result):
    status = result["status"]
    item = result.get("item")
    if status == "claimed":
        msg = (
            "*CLAIM DETAILS*\n"
            "----------------------------\n"
            f"Item    : {item}\n"
            f"Server  : {acc['server_name']}\n"
            f"Email   : {acc['email']}\n"
            "----------------------------"
        )
    elif status == "already_claimed":
        msg = (f"ALREADY CLAIMED\nAccount: {acc['email']}\nCome back tomorrow~")
    elif status == "server_not_found":
        msg = ("SERVER NOT FOUND\n"
               f"Account: {acc['email']}\n"
               f"Expected: {acc['server_name']}\n"
               f"Available: {', '.join(result.get('available', []))}")
    else:
        msg = f"Unknown status for {acc['email']}: {status}"
    logger.info(msg)
    send_telegram_message(msg)


def dump_diagnostics(driver, label):
    """On failure, capture page state for debugging (workflow log + artifacts).

    NOTE: page_source never contains password field values. Logged body text is
    capped and is the challenge/block page, not credentials.
    """
    try:
        url = driver.current_url
        title = driver.title
        body = ""
        try:
            body = driver.find_element(By.TAG_NAME, "body").text[:600]
        except Exception:
            pass
        logger.error(f"[DIAG {label}] url={url} | title={title!r}")
        logger.error(f"[DIAG {label}] body_snippet={body!r}")
        os.makedirs("diagnostics", exist_ok=True)
        safe = "".join(c if c.isalnum() else "_" for c in label)[:40]
        with open(f"diagnostics/{safe}.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        driver.save_screenshot(f"diagnostics/{safe}.png")
        logger.info(f"[DIAG {label}] saved diagnostics/{safe}.html and .png")
    except Exception as e:
        logger.error(f"[DIAG {label}] failed to capture diagnostics: {e}")


def process_account(acc, idx):
    driver = build_driver()
    wait = WebDriverWait(driver, 25)
    try:
        logger.info(f"Processing {acc['email']}")
        login(driver, wait, acc["email"], acc["password"])
        notify(acc, claim(driver, wait, acc["server_name"]))
    except TimeoutException as e:
        logger.error(f"Timeout for {acc['email']}: {e}")
        dump_diagnostics(driver, f"account{idx}_timeout")
        send_telegram_message(f"Timeout for {acc['email']} -- site slow or layout changed.")
    except Exception as e:
        logger.error(f"Error for {acc['email']}: {e}")
        dump_diagnostics(driver, f"account{idx}_error")
        send_telegram_message(f"Error for {acc['email']}: {str(e)[:200]}")
    finally:
        driver.quit()


def main():
    accounts = load_accounts()
    if not accounts:
        logger.error("No accounts. Set EMAIL1/PASSWORD1/SERVER_NAME1 (+ TELEGRAM_*) env vars.")
        return
    for idx, acc in enumerate(accounts, start=1):
        process_account(acc, idx)


if __name__ == "__main__":
    main()
