import aiohttp
import asyncio
import aiofiles
import pandas as pd
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from tqdm.asyncio import tqdm
import os

INPUT_FILE = "input.csv"
OUTPUT_FILE = "output.csv"
MAX_CONCURRENT_REQUESTS = 200  # 同時接続数（回線に応じて調整）

# ターゲットキーワード
KEYWORDS = ["contact", "contacts", "inquiry", "お問い合わせ", "コンタクトフォーム"]

# セマフォ（同時リクエスト制限）
semaphore = asyncio.Semaphore(MAX_CONCURRENT_REQUESTS)

# contact URL 抽出関数
def extract_contact_url(base_url, html):
    soup = BeautifulSoup(html, "html.parser")
    for a in soup.find_all("a", href=True):
        href = a["href"].lower()
        text = a.get_text().lower()
        if any(k in href or k in text for k in KEYWORDS):
            return urljoin(base_url, a["href"])
    return ""

# 各URLの非同期処理
async def process(session, company_name, url):
    async with semaphore:
        try:
            async with session.get(url, timeout=10) as response:
                if response.status == 200:
                    html = await response.text()
                    contact_url = extract_contact_url(url, html)
                    return {"company_name": company_name, "url": url, "contact_url": contact_url}
        except Exception:
            pass
        return {"company_name": company_name, "url": url, "contact_url": ""}

# メイン処理
async def main():
    df = pd.read_csv(INPUT_FILE)
    tasks = []

    connector = aiohttp.TCPConnector(limit_per_host=MAX_CONCURRENT_REQUESTS)
    headers = {"User-Agent": "Mozilla/5.0"}

    async with aiohttp.ClientSession(connector=connector, headers=headers) as session:
        for _, row in df.iterrows():
            task = asyncio.create_task(process(session, row["company_name"], row["url"]))
            tasks.append(task)

        results = []
        for f in tqdm(asyncio.as_completed(tasks), total=len(tasks), desc="📡 処理中"):
            result = await f
            results.append(result)

    # 出力
    pd.DataFrame(results).to_csv(OUTPUT_FILE, index=False)
    print(f"完了！結果を保存しました: {OUTPUT_FILE}")

# 実行エントリポイント
if __name__ == "__main__":
    asyncio.run(main())
