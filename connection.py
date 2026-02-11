from google import genai
from dotenv import load_dotenv
import os

# .envファイルから環境変数を読み込む
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

# クライアントの初期化
client = genai.Client(api_key=api_key)

try:
    # あなたのリストに存在した 'gemini-flash-latest' を使用します
    response = client.models.generate_content(
        model='gemini-flash-latest', 
        contents="接続テストです。このモデルで応答可能か確認しています。一言お願いします！"
    )
    
    print("--- Geminiからのメッセージ ---")
    print(response.text)
    print("----------------------------")
    print("✨ 接続成功です！ようやく心臓部が動き出しました。")

except Exception as e:
    print(f"接続エラーが発生しました: {e}")