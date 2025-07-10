import pandas as pd
from datetime import datetime
import os

# Excelファイル名
excel_file = "appointment_list.xlsx"

# ユーザー入力
new_name = input("登録したい名前を入力してください（new_name）：")
user_name = input("あなたの名前を入力してください（user_name）：")

# ファイルの存在確認
if os.path.exists(excel_file):
    df = pd.read_excel(excel_file, engine='openpyxl')
else:
    df = pd.DataFrame(columns=["名前", "登録日時", "担当者"])

# 重複チェック
if new_name in df["名前"].values:
    existing_index = df[df["名前"] == new_name].index[0]
    existing_entry = df.loc[existing_index]
    print(f"⚠️ 名前「{new_name}」はすでに登録されています。")
    print(f"登録者：{existing_entry['担当者']}（{existing_entry['登録日時']}）")
    confirm = input("それでも登録しますか？（はい/いいえ）：").strip().lower()
    if confirm == "はい":
        # 既存行を更新
        df.at[existing_index, "担当者"] = user_name
        df.at[existing_index, "登録日時"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"✅ 名前「{new_name}」の登録情報を更新しました。")
    else:
        print("登録をキャンセルしました。")
        exit()
else:
    # 新規登録処理
    new_entry = pd.DataFrame([{
        "名前": new_name,
        "登録日時": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "担当者": user_name
    }])
    df = pd.concat([df, new_entry], ignore_index=True)
    print(f"✅ 名前「{new_name}」を新規登録しました。")

# Excelファイルに保存
df.to_excel(excel_file, index=False, engine='openpyxl')
print("Excelファイルを更新しました。")
