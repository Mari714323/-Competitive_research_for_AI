import os
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process
from crewai.tools import tool
from search_tool import search_competitors # 先ほど作ったツールをインポート

# 1. 環境変数の読み込み
load_dotenv()

# 2. カスタムツールの設定
# AIエージェントがこの関数を「検索ツール」として使えるように定義します
@tool("WebSearch")
def search_tool(query: str):
    """最新の競合サービスや類似製品をインターネットで検索するために使用します。"""
    # 先ほど作った search_competitors 関数を呼び出す
    return search_competitors(query)

# 3. エージェントの定義
# 脳（LLM）の設定。リストにあった安定モデルを指定
gemini_llm = "gemini/gemini-flash-latest" 

researcher = Agent(
    role='競合調査リサーチャー',
    goal='指定された業種や製品について、市場の主要な競合サービスを5つ見つけ出す',
    backstory='あなたは市場分析のスペシャリストです。最新のトレンドを把握し、隠れた優良サービスを見つけ出すことに長けています。',
    tools=[search_tool], # @tool で定義した関数をそのまま渡せます
    llm=gemini_llm,
    verbose=True
)

writer = Agent(
    role='ビジネスアナリスト',
    goal='リサーチ結果を比較表形式でまとめ、特徴や弱点を分析する',
    backstory='あなたは複雑な情報を整理し、意思決定に役立つレポートを作成するプロフェッショナルです。',
    llm=gemini_llm,
    verbose=True
)

# 4. タスクの定義
research_task = Task(
    description='「個人向けのタスク管理アプリ」の市場を調査し、競合サービスを5つリストアップしてください。',
    expected_output='各サービスの名称、URL、主な特徴を含む詳細なリサーチ結果。',
    agent=researcher
)

analysis_task = Task(
    description='リサーチ結果をもとに、それぞれのサービスの強みと弱点を分析し、最後に比較表（マークダウン形式）を作成してください。',
    expected_output='各サービスの分析内容と比較表。',
    agent=writer
)

# 5. クルーの結成と実行
crew = Crew(
    agents=[researcher, writer],
    tasks=[research_task, analysis_task],
    process=Process.sequential # 順番に実行（リサーチ → 分析）
)

print("--- エージェントが調査を開始します ---")
result = crew.kickoff()

print("\n\n########################")
print("## 最終レポート")
print("########################\n")
print(result)