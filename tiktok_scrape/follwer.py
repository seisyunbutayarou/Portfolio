from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import urllib.parse
import time
import csv
import re

CHROMEDRIVER_PATH = r""

options = Options()
options.add_argument("--disable-gpu")
options.add_argument("--window-size=1920,1080")
options.add_argument("--lang=ja-JP")

service = Service(CHROMEDRIVER_PATH)
driver = webdriver.Chrome(service=service, options=options)

input_file = "filtered_tiktok_users.csv"
output_file = "filtered_tiktok_users_with_followers.csv"

updated_data = []

with open(input_file, "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    wait = WebDriverWait(driver, 5)

    for i, row in enumerate(reader, 1):
        profile_url = row["profile_url"]
        print(f"[{i}] アクセス中: {profile_url}")
        driver.get(profile_url)

        try:
            # フォロワー数
            follower_element = wait.until(
                EC.presence_of_element_located((By.XPATH, "//strong[@data-e2e='followers-count']"))
            )
            follower_text = follower_element.text.strip()
            if "K" in follower_text:
                follower_count = int(float(follower_text.replace("K", "")) * 1000)
            elif "M" in follower_text:
                follower_count = int(float(follower_text.replace("M", "")) * 1000000)
            else:
                follower_count = int(follower_text.replace(",", ""))
            row["follower_count"] = follower_count

            # いいね数
            likes_element = driver.find_element(By.XPATH, "//strong[@data-e2e='likes-count']")
            likes_text = likes_element.text.strip()
            if "K" in likes_text:
                likes_count = int(float(likes_text.replace("K", "")) * 1000)
            elif "M" in likes_text:
                likes_count = int(float(likes_text.replace("M", "")) * 1000000)
            else:
                likes_count = int(likes_text.replace(",", ""))
            row["likes_count"] = likes_count

            # 自己紹介文とリンク抽出
            try:
                bio_element = driver.find_element(By.XPATH, "//h2[@data-e2e='user-bio']")
                bio_text = bio_element.text.strip()
                row["bio"] = bio_text

                # Instagramリンク抽出（文脈あり）
                instagram_url = ""
                if re.search(r"インスタ|insta", bio_text, re.IGNORECASE):
                    match_url = re.search(r"(https?://(?:www\.)?instagram\.com/[^\s]+)", bio_text)
                    match_at = re.search(r"@([a-zA-Z0-9._]+)", bio_text)
                    match_username = re.search(r"(?:インスタグラム|インスタ|insta)[^\w@]*([a-zA-Z0-9._]{3,})", bio_text, re.IGNORECASE)

                    if match_url:
                        instagram_url = match_url.group(1)
                    elif match_at:
                        instagram_url = f"https://www.instagram.com/{match_at.group(1)}"
                    elif match_username:
                        instagram_url = f"https://www.instagram.com/{match_username.group(1)}"
                row["instagram_url"] = instagram_url

                # 外部リンク（楽天ROOMなど）抽出
                external_link = ""
                try:
                    external_link_el = driver.find_element(By.XPATH, "//a[@data-e2e='user-link']")
                    raw_href = external_link_el.get_attribute("href")
                    # TikTokのリダイレクトURLから本来のリンクを抽出
                    match_target = re.search(r"target=(https%3A%2F%2F[^\s]+)", raw_href)
                    if match_target:
                        decoded_url = urllib.parse.unquote(match_target.group(1))
                        external_link = decoded_url
                    else:
                        external_link = raw_href
                except:
                    external_link = ""
                row["external_link"] = external_link

            except:
                row["bio"] = ""
                row["instagram_url"] = ""
                row["external_link"] = ""

        except Exception as e:
            print(f"  → 情報取得失敗: {e}")
            row["follower_count"] = "取得失敗"
            row["likes_count"] = "取得失敗"
            row["bio"] = ""
            row["instagram_url"] = ""
            row["external_link"] = ""

        updated_data.append(row)

# 保存（UTF-8 BOM付きでExcel対応）
with open(output_file, "w", newline="", encoding="utf-8-sig") as f:
    fieldnames = list(updated_data[0].keys())
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(updated_data)

driver.quit()
print("✅ 情報付きCSVを保存しました。")
