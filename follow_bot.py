# Fix logic for scroll, maybe screen captures, current code needs to be updated according to instagrams shoddy code updates

import time
import random
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options

# Passwords here
USERNAME = ""
PASSWORD = ""
TARGET = ""
MAX_FOLLOWS = 1000


def human_delay(a=2, b=4):
    time.sleep(random.uniform(a, b))

def setup_browser():
    options = Options()
    options.add_argument("--headless")
    return webdriver.Chrome(options=options)

def login(driver):
    driver.get("https://www.instagram.com/accounts/login/")
    human_delay(3, 6)
    driver.find_element(By.NAME, "username").send_keys(USERNAME)
    driver.find_element(By.NAME, "password").send_keys(PASSWORD + Keys.RETURN)
    human_delay(5, 7)
    print("[INFO] Logged in.")

def follow_from_scrollbox(driver):
    print("[INFO] Navigating to following list...")
    driver.get(f"https://www.instagram.com/{TARGET}/")  
    wait = WebDriverWait(driver, 15)

    try:
        following_link = wait.until(EC.presence_of_element_located((By.PARTIAL_LINK_TEXT, "following")))
        following_link.click()
    except Exception as e:
        print(f"[ERROR] Could not find 'following' link: {e}")
        return

    human_delay(3, 5)

    scroll_box = wait.until(EC.presence_of_element_located(
        (By.XPATH, "//div[@role='dialog']//div[contains(@class, 'x7r02ix')]")
    ))

    followed_set = set()
    followed_count = 0
    unchanged_scrolls = 0
    max_empty_scrolls = 1000

    print("[INFO] Scanning for followable users...")

    while followed_count < MAX_FOLLOWS and unchanged_scrolls < max_empty_scrolls:
        buttons = scroll_box.find_elements(By.XPATH, ".//div[text()='Follow' and contains(@class, '_ap3a')]")
        print(f"[DEBUG] Found {len(buttons)} follow buttons.")

        if not buttons:
            driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", scroll_box)
            human_delay(2, 3)
            unchanged_scrolls += 1
            continue
        else:
            unchanged_scrolls = 0

        for btn in buttons:
            try:
                ancestor = btn.find_element(By.XPATH, "./../../../../..")
                username_el = ancestor.find_element(By.TAG_NAME, "a")
                profile_url = username_el.get_attribute("href")
                username = profile_url.rstrip("/").split("/")[-1]

                if username in followed_set:
                    continue

                # fix verification badge logic, svg doesnt work, instagram sucks
                is_verified = False
                try:
                    badge_icon = ancestor.find_element(By.XPATH, ".//svg//*[name()='path']")
                    if badge_icon:
                        is_verified = True
                except:
                    pass

                if is_verified:
                    print(f"[SKIP] Verified account: {username}")
                    continue

                driver.execute_script("arguments[0].scrollIntoView(true);", btn)
                human_delay(1, 2)

                btn.click()
                followed_set.add(username)
                followed_count += 1
                print(f"[FOLLOWED] ({followed_count}) {username}")
                human_delay(3, 5)

                if followed_count >= MAX_FOLLOWS:
                    break

            except Exception as e:
                print(f"[SKIP] Error processing button: {e}")
                continue

    print(f"[INFO] Done. Total followed: {followed_count}")


if __name__ == "__main__":
    driver = setup_browser()
    login(driver)
    follow_from_scrollbox(driver)
    driver.quit()
    print("[INFO] All done.")
