import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
import pytz

USERNAME = ""
N_RECENT = 20

TWITTER_EMAIL = ""
TWITTER_PASSWORD = ""
actual_username = ""

def init_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    driver = webdriver.Chrome(options=options)
    return driver

def login_to_x(driver, email, password):
    driver.get("https://x.com/login")
    WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.NAME, "text")))

    email_input = driver.find_element(By.NAME, "text")
    email_input.send_keys(email)
    email_input.send_keys(Keys.RETURN)
    time.sleep(3)

    try:
        username_input = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.NAME, "text"))
        )
        username_input.send_keys(actual_username)
        username_input.send_keys(Keys.RETURN)
        time.sleep(3)
    except:
        print("ユーザー名入力スキップ")

    try:
        password_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "password"))
        )
        password_input.send_keys(password)
        password_input.send_keys(Keys.RETURN)
        time.sleep(5)
    except:
        print("パスワード入力失敗（2段階認証など）")

def scrape_latest_tweets(driver, username, max_tweets=10):
    url = f"https://x.com/{username}?f=live"
    driver.get(url)
    WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH, "//article")))
    time.sleep(5)

    tweets = []
    seen_ids = set()
    scroll_attempts = 0
    max_scroll_attempts = 100

    while len(tweets) < max_tweets and scroll_attempts < max_scroll_attempts:
        articles = driver.find_elements(By.XPATH, "//article")

        for article in articles:
            try:
                tweet_link_elem = article.find_element(By.XPATH, ".//a[contains(@href, '/status/')]")
                tweet_url = tweet_link_elem.get_attribute("href")
                tweet_id = tweet_url.split("/")[-1]

                if tweet_id in seen_ids:
                    continue

                text_elem = article.find_element(By.XPATH, ".//div[@data-testid='tweetText']")
                tweet_text = text_elem.text

                time_elem = article.find_element(By.XPATH, ".//time")
                timestamp = time_elem.get_attribute("datetime")

                reply_to = ""
                content = article.text.lower()
                if "返信先" in content or "replying to" in content:
                    reply_lines = [line for line in content.split("\n") if "@" in line]
                    reply_to = reply_lines[0] if reply_lines else ""

                # 画像URLの抽出
                image_elems = article.find_elements(By.XPATH, ".//img[contains(@src, 'twimg.com/media')]")
                image_urls = list({img.get_attribute("src") for img in image_elems})

                tweets.append({
                    "tweet_id": tweet_id,
                    "tweet_text": tweet_text,
                    "timestamp": timestamp,
                    "reply_to": reply_to,
                    "image_urls": ", ".join(image_urls)
                })
                seen_ids.add(tweet_id)

                if len(tweets) >= max_tweets:
                    break
            except:
                continue

        # スクロールと待機
        if len(tweets) < max_tweets:
            driver.execute_script("window.scrollBy(0, 500);")
            time.sleep(1.5)
            scroll_attempts += 1

    return tweets


if __name__ == "__main__":
    driver = init_driver()
    try:
        login_to_x(driver, TWITTER_EMAIL, TWITTER_PASSWORD)
        time.sleep(5)

        data = scrape_latest_tweets(driver, USERNAME, max_tweets=N_RECENT)
        df = pd.DataFrame(data)

        df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True, errors='coerce')
        df = df.dropna(subset=["timestamp"])
        df = df.sort_values("timestamp", ascending=False).head(N_RECENT)

        for _, row in df.iterrows():
            print("本文:", row["tweet_text"])
            print("ツイートID:", row["tweet_id"])
            print("投稿日時:", row["timestamp"])
            print("リプライ先:", row["reply_to"])
            print("画像URL:", row["image_urls"])
            print("-" * 30)

        filename = f"{USERNAME}_latest_{N_RECENT}_tweets.csv"
        df[["tweet_text", "tweet_id", "timestamp", "reply_to", "image_urls"]].to_csv(filename, index=False, encoding="utf-8-sig")
        print(f"✅ 直近{len(df)}件のツイートを取得し、{filename} に保存しました。")
    finally:
        driver.quit()
