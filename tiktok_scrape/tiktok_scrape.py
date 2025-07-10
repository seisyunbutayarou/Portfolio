from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
import csv

CHROMEDRIVER_PATH = r""

options = Options()
options.add_argument("--disable-gpu")
options.add_argument("--window-size=1920,1080")
options.add_argument("--lang=ja-JP")

service = Service(CHROMEDRIVER_PATH)
driver = webdriver.Chrome(service=service, options=options)

driver.get("https://www.tiktok.com/explore?lang=ja-JP")
time.sleep(2)

# 美容ケアボタンをクリック
beauty_button = driver.find_element(By.XPATH, "//span[text()='美容ケア']/parent::button")
beauty_button.click()
time.sleep(2)

# ページをスクロールしてユーザーを読み込む
SCROLL_PAUSE_TIME = 1
MAX_SCROLLS = 5

last_height = driver.execute_script("return document.body.scrollHeight")
for i in range(MAX_SCROLLS):
    print(f"スクロール {i+1}/{MAX_SCROLLS}")
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(SCROLL_PAUSE_TIME)
    new_height = driver.execute_script("return document.body.scrollHeight")
    if new_height == last_height:
        break
    last_height = new_height

# ユーザーカードの取得
user_cards = driver.find_elements(By.XPATH, "//div[contains(@class, 'css-e2juzq-DivCardBottomInfo')]")

user_data = []

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

wait = WebDriverWait(driver, 5)  # 最大5秒待機

for card in user_cards:
    try:
        username_el = card.find_element(By.XPATH, './/*[@data-e2e="explore-card-user-unique-id"]')
        link_el = card.find_element(By.XPATH, './/*[@data-e2e="explore-card-user-link"]')
        avatar_el = card.find_element(By.XPATH, './/*[contains(@class, "ImgAvatar")]')

        username = username_el.text
        href = link_el.get_attribute("href")
        profile_url = href if href.startswith("https://") else "https://www.tiktok.com" + href
        avatar_url = avatar_el.get_attribute("src")

        if username and profile_url and avatar_url:
            user_data.append({
                "username": username,
                "profile_url": profile_url,
                "avatar_url": avatar_url
            })

    except Exception as e:
        print(f"エラー: {e}")
        continue



with open("filtered_tiktok_users.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["username", "profile_url", "avatar_url"])
    writer.writeheader()
    writer.writerows(user_data)

driver.quit()
print("ユーザー情報をCSVに保存しました。")

