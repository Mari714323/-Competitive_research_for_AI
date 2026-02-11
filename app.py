import streamlit as st
import pandas as pd
from crewai import Crew, Process
from main import researcher, writer, research_task, analysis_task # main.pyから流用
import io

# --- ページ設定 ---
st.set_page_config(page_title="AI 競合調査エージェント", layout="wide")

st.title("🤖 AI 競合調査エージェント")
st.markdown("調査したい製品やサービス名を入力すると、AIがネットから情報を集めて分析レポートを作成します。")

# --- サイドバー：設定 ---
with st.sidebar:
    st.header("設定")
    topic = st.text_input("調査対象の業種・製品", placeholder="例：個人向けタスク管理アプリ")
    search_limit = st.slider("検索上限数", 1, 10, 5)

# --- メイン画面：実行ボタン ---
if st.button("調査を開始する", type="primary"):
    if not topic:
        st.warning("調査対象を入力してください。")
    else:
        with st.status("🚀 AIエージェントが調査中...", expanded=True) as status:
            # タスクの内容を画面の入力内容で上書き
            research_task.description = f"「{topic}」の市場を調査し、競合サービスを{search_limit}つリストアップしてください。"
            
            # クルーの結成と実行
            crew = Crew(
                agents=[researcher, writer],
                tasks=[research_task, analysis_task],
                process=Process.sequential
            )
            
            # 実行
            result = crew.kickoff()
            status.update(label="✅ 調査完了！", state="complete", expanded=False)

        # --- 結果の表示 ---
        st.header("📋 調査レポート")
        st.markdown(result)

        # --- 次回予告：Excel/CSV出力機能の土台 ---
        st.divider()
        st.info("※ここにフィルタリング機能やExcel出力ボタンを実装していきます。")