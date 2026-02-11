import streamlit as st
import pandas as pd
from crewai import Crew, Process
from main import researcher, writer, research_task, analysis_task # main.pyから流用
import io
import json

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
# --- app.py 修正版 (ボタン部分) ---

# --- app.py 修正箇所 ---

if st.button("調査を開始する", type="primary"):
    if not topic:
        st.warning("調査対象を入力してください。")
    else:
        # セッションの初期化
        st.session_state['df'] = None
        st.session_state['report'] = None
            
        with st.status("🚀 AIエージェントが1回限りのリサーチを実行中...") as status:
            # AIに「何度も考えず、1回で結果を出せ」と強く指示
            research_task.description = f"「{topic}」の競合サービスを{search_limit}つ見つけ出し、名称とURLを特定してください。追加の検索は不要です。"
            analysis_task.description = (
                "受け取ったデータを元に簡単な分析レポートを書き、"
                "末尾に必ず [{\"サービス名\": \"...\", \"URL\": \"...\", \"特徴\": \"...\"}] 形式のJSONを出力してください。"
            )
            
            crew = Crew(
                agents=[researcher, writer],
                tasks=[research_task, analysis_task],
                process=Process.sequential
            )
            
            # 実行（この1回に今日の運命をかけます）
            result = crew.kickoff(inputs={'topic': topic})
            
            # --- JSON抽出処理 ---
            try:
                import re
                res_str = str(result.raw)
                json_match = re.search(r'\[.*\]', res_str, re.DOTALL)
                if json_match:
                    data = json.loads(json_match.group())
                    st.session_state['df'] = pd.DataFrame(data)
                    st.session_state['report'] = res_str
                    status.update(label="✅ 完了！", state="complete")
                else:
                    st.error("データの抽出に失敗しました。")
            except Exception as e:
                st.error(f"解析エラー: {e}")