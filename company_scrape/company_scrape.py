import os
import time
import csv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# ChromeDriverのパス
CHROMEDRIVER_PATH = r""

# 検索キーワード
search_keyword = ""

# 保存先CSVファイル
csv_file = "tiktok_user_url.csv"

# Chromeオプション設定
options = Options()
# options.add_argument("--headless=new")  # 必要に応じて有効化
options.add_argument("--disable-gpu")
options.add_argument("--window-size=1920,1080")
options.add_argument("--lang=ja-JP")
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36")

# ドライバー起動
service = Service(CHROMEDRIVER_PATH)
driver = webdriver.Chrome(service=service, options=options)
wait = WebDriverWait(driver, 15)

# TikTok検索ページにアクセス
driver.get(f"https://www.tiktok.com/search?q={search_keyword}")
time.sleep(3)

# 既存ユーザー名の読み込み
seen_usernames = set()
if os.path.exists(csv_file):
    with open(csv_file, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            seen_usernames.add(row["username"])

# スクロール設定
SCROLL_PAUSE_TIME = 1
MAX_SCROLLS = 30
user_data = []
previous_usernames = set()

for i in range(MAX_SCROLLS):
    print(f"✅ スクロール {i+1}/{MAX_SCROLLS}")
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    try:
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'a[data-e2e="search-card-user-link"]')))
    except:
        print("⚠️ 新しい要素が読み込まれませんでした。")

    time.sleep(SCROLL_PAUSE_TIME)

    # JavaScriptでユーザー情報を取得
    results = driver.execute_script("""
        return Array.from(document.querySelectorAll('a[data-e2e="search-card-user-link"]')).map(el => {
            const usernameEl = el.querySelector('p[data-e2e="search-card-user-unique-id"]');
            const username = usernameEl ? usernameEl.innerText : null;
            const href = el.href.startsWith("http") ? el.href : "https://www.tiktok.com" + el.getAttribute("href");
            return { username, href };
        });
    """)

    current_usernames = set(item["username"] for item in results if item["username"])
    new_usernames = current_usernames - previous_usernames

    if not new_usernames:
        print("これ以上スクロールできません。スクロールを終了します。")
        break

    previous_usernames.update(current_usernames)

    for item in results:
        username = item["username"]
        profile_url = item["href"]
        if username and profile_url and username not in seen_usernames:
            user_data.append({"username": username, "profile_url": profile_url})
            seen_usernames.add(username)

# 新規ユーザーをCSVに保存
with open(csv_file, "a", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["username", "profile_url"])
    if f.tell() == 0:
        writer.writeheader()
    writer.writerows(user_data)

driver.quit()
print(f"✅ {len(user_data)} 件の新規ユーザーネームとURLをCSVに追加しました。")