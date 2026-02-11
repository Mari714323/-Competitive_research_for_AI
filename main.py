# --- main.py (修正版) ---
import os
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process
from crewai.tools import tool
from search_tool import search_competitors

load_dotenv()

@tool("WebSearch")
def search_tool(query: str):
    """最新の競合サービスや類似製品をインターネットで検索するために使用します。"""
    return search_competitors(query)

# 3. エージェントの定義
# --- main.py 修正箇所 ---

# 以前成功した名称に統一します
gemini_llm = "gemini/gemini-flash-latest" 

researcher = Agent(
    role='競合調査リサーチャー',
    goal='指定された製品の競合サービスをリストアップする',
    backstory='あなたは迅速な調査を最優先するプロフェッショナルです。',
    tools=[search_tool],
    llm=gemini_llm,
    # 【重要】AIの「自問自答」を最大1回に制限し、API消費を極限まで抑えます
    max_iter=1, 
    # 【重要】他のエージェントに相談（API消費）させない設定
    allow_delegation=False,
    verbose=True
)

writer = Agent(
    role='ビジネスアナリスト',
    goal='リサーチ結果を分析し、JSON形式のリストを作成する',
    backstory='あなたは情報を整理するプロフェッショナルです。',
    llm=gemini_llm,
    max_iter=1, # こちらも最小限に
    allow_delegation=False,
    verbose=True
)

# 実行ガード（app.pyからのインポート時にAIが動くのを防ぎます）
if __name__ == "__main__":
    pass # ターミナルからは実行しない