import json
import os
import re

HISTORY_FILE = "history.json"

def load_history_data():
    """履歴ファイルを読み込む"""
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_history_data(topic, report, df_data):
    """結果を履歴ファイルに保存する"""
    history = load_history_data()
    history[topic] = {
        "report": report,
        "df_data": df_data
    }
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=4)

def clean_topic_name(text):
    """ファイル名に使えない文字を除去して安全なトピック名にする"""
    return re.sub(r'[\\/:*?"<>|]+', '', text)

# src/utils.py の該当関数をこれに書き換え

def extract_json_from_text(text):
    """テキスト内にあるJSONブロック({...}や[...])を抽出する"""
    try:
        # パターン1: マークダウンのコードブロック ```json ... ``` で囲まれている場合
        code_block_match = re.search(r'```json\s*(.*?)\s*```', text, re.DOTALL)
        if code_block_match:
            json_str = code_block_match.group(1)
            return json.loads(json_str)

        # パターン2: 直接書かれている場合
        # 普通の [ ] だと引用 [1] などに反応してしまうため、
        # 「 [ の直後に { がある（間に空白・改行OK）」というパターンを探す
        json_match = re.search(r'(\[\s*\{.*\}\s*\])', text, re.DOTALL)
        if json_match:
            json_str = json_match.group(1)
            return json.loads(json_str)
            
    except Exception as e:
        # デバッグ用: 解析失敗の理由をターミナルに出しても良い
        print(f"JSON Parse Error: {e}")
        pass
    
    return None

def split_report_by_agent(report_text):
    """レポートをエージェントごとのセクションに分割する"""
    try:
        # splitの結果は [前置き, 名前1, 内容1, 名前2, 内容2...] というリストになります
        sections = re.split(r'## 👤 (.*?) の報告\n\n', report_text)
        if len(sections) > 1:
            roles = sections[1::2]
            contents = sections[2::2]
            return roles, contents
    except Exception:
        pass
    return [], []