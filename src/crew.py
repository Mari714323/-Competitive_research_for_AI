# --- main.py (修正版) ---
import os
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process
from crewai.tools import tool
from src.tools import search_competitors

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

# 4. タスクの定義
research_task = Task(
    description='「{topic}」の市場を調査し、競合サービスをリストアップしてください。',
    expected_output='各サービスの名称、URL、主な特徴。',
    agent=researcher
)

analysis_task = Task(
    description='リサーチ結果をもとに強みと弱点を分析し、最後に必ず指定されたJSON形式のリストを末尾に含めてください。',
    expected_output='分析レポートと、[{"サービス名": "...", "URL": "...", "特徴": "..."}] 形式のJSONデータ。',
    agent=writer
)

# 実行ガード（app.pyからのインポート時にAIが動くのを防ぎます）
if __name__ == "__main__":
    pass # ターミナルからは実行しない

# 3人目のエージェント：戦略コンサルタント
strategist = Agent(
    role='戦略コンサルタント',
    goal='競合調査レポートを元に、SWOT分析と具体的な戦略提案を行う',
    backstory='あなたはMBAを持つ経験豊富な戦略コンサルタントです。市場の機会と脅威を鋭く読み解き、実行可能な戦略を立案するのが得意です。',
    llm=gemini_llm,
    max_iter=1,
    allow_delegation=False,
    verbose=True
)

# 3つ目のタスク：戦略立案
strategy_task = Task(
    description='これまでの調査結果と分析リストを元に、「{topic}」のSWOT分析（強み・弱み・機会・脅威）を行ってください。また、それに基づいた具体的な差別化戦略を3つ提案してください。',
    expected_output='SWOT分析表（Markdown形式）と、3つの戦略提案を含んだ詳細なレポート。',
    agent=strategist,
    context=[research_task, analysis_task] # 前のタスクの結果を参照させる
)