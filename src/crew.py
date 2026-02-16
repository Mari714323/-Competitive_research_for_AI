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
    description='「{topic}」の市場を調査し、主要な競合サービスやトレンドをリストアップしてください。検索結果が英語であっても、報告は必ず日本語で行ってください。',
    expected_output='市場の概要、主要な競合リスト（名称と特徴）、トレンドをまとめた日本語のレポート。', # ★ここを具体的に修正
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

# 4人目：リーン・スタートアップ・コーチ
coach = Agent(
    role='スタートアップ・コーチ',
    goal='調査結果を元に、具体的で実行可能な「最初のアクションプラン」を提案する',
    backstory='あなたは数々の起業家を成功に導いたメンターです。「リーン・スタートアップ」の精神に基づき、無駄なく素早く仮説検証を行うためのステップを助言します。',
    llm=gemini_llm,
    max_iter=1,
    allow_delegation=False,
    verbose=True
)

# コーチのタスク
coach_task = Task(
    description='これまでの調査と分析を踏まえ、「{topic}」で起業するための「最初の1ヶ月のアクションプラン」を作成してください。MVP（検証用製品）の定義、顧客ヒアリングの質問リスト、最初のアプローチ方法などを具体的に提案してください。',
    expected_output='1ヶ月間の週ごとのアクションリストと、検証すべき仮説リスト。',
    agent=coach,
    context=[research_task, analysis_task, strategy_task]
)

# 5人目：辛口なターゲットユーザー（ペルソナ）
persona = Agent(
    role='辛口なターゲットユーザー',
    goal='ユーザー視点で、サービスを使いたいか、いくらなら払うかを本音でフィードバックする',
    backstory='あなたは新しいもの好きですが、財布の紐は固い一般ユーザーです。企業側の都合のいい理屈は一切通用しません。「自分にとってメリットがあるか」だけで厳しく判断します。',
    llm=gemini_llm,
    max_iter=1,
    allow_delegation=False,
    verbose=True
)

# ペルソナのタスク
persona_task = Task(
    description='あなたは「{topic}」の潜在的な顧客です。提案されているサービスや競合情報を見て、「自分ならこれを使うか？」「お金を払うか？」を本音で語ってください。良い点だけでなく、不満や懸念点も遠慮なく挙げてください。',
    expected_output='ユーザー視点の率直な感想、良い点・悪い点のフィードバック、利用意向の有無。',
    agent=persona,
    context=[research_task] # 調査結果だけ見せればOK
)

# 6人目：プロダクトマネージャー（要件定義）
pdm = Agent(
    role='プロダクトマネージャー',
    goal='曖昧なアイデアから、開発可能なレベルの「要件定義書」を作成する',
    backstory='あなたは仕様策定のプロフェッショナルです。「何を作るか」を明確にし、抜け漏れのない機能リストと画面設計を定義します。開発者が迷わず実装できるドキュメント品質にこだわります。',
    llm=gemini_llm,
    max_iter=1,
    allow_delegation=False,
    verbose=True
)

# PdMのタスク
requirements_task = Task(
    description='「{topic}」のアイデアを元に、詳細な「要件定義書」を作成してください。以下の項目を含めてください：\n1. ユーザーストーリー（誰が何をしてどうなるか）\n2. 機能要件リスト（Must/Wantで優先度付け）\n3. 必要な画面リストとその機能',
    expected_output='Markdown形式の要件定義書。',
    agent=pdm
)

# 7人目：テックリード（基本設計）
architect = Agent(
    role='テックリード',
    goal='要件定義を元に、最適な技術選定と「基本設計書」を作成する',
    backstory='あなたはモダンな技術に精通したフルスタックエンジニアです。個人開発の規模感に合わせ、開発効率と保守性を両立できる技術選定（Next.js, Supabase, FastAPIなど）や、具体的なデータ構造の設計が得意です。',
    llm=gemini_llm,
    max_iter=1,
    allow_delegation=False,
    verbose=True
)

# テックリードのタスク
design_task = Task(
    description='要件定義書を元に、このアプリを開発するための「基本設計書」を作成してください。以下の項目を含めてください：\n1. 推奨技術スタック（Frontend, Backend, DB, Infra）とその選定理由\n2. データベース設計（テーブル定義とリレーションのER図イメージ）\n3. 主要なAPIエンドポイントの設計',
    expected_output='Markdown形式の基本設計書（mermaid記法のER図を含む）。',
    agent=architect,
    context=[requirements_task] # PdMの成果物を参照させる
)