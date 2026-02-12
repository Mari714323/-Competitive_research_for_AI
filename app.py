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
if st.button("調査を開始する", type="primary"):
    if not topic:
        st.warning("調査対象を入力してください。")
    else:
        # 実行前に前回の結果をクリアして真っさらにする
        # 実行前に前回の結果をクリア
        st.session_state['df'] = None
        st.session_state['report'] = None
        # ★追加: ファイル名用にトピックを保存しておく
        st.session_state['topic'] = topic
            
        with st.status("🚀 AIエージェントが調査中...") as status:
            # タスク指示
            research_task.description = f"「{topic}」の市場を調査し、競合サービスをリストアップしてください。"
            analysis_task.description = "レポートを作成し、最後に必ず [{\"サービス名\": \"...\", \"URL\": \"...\", \"特徴\": \"...\"}] 形式のJSONを含めてください。"
            
            crew = Crew(agents=[researcher, writer], tasks=[research_task, analysis_task])
            result = crew.kickoff(inputs={'topic': topic})
            
            st.session_state['report'] = str(result.raw)
            
            # JSONデータの抽出
            try:
                import re
                json_match = re.search(r'\[.*\]', str(result.raw), re.DOTALL)
                if json_match:
                    data = json.loads(json_match.group())
                    st.session_state['df'] = pd.DataFrame(data)
                    status.update(label="✅ 調査完了！", state="complete")
                else:
                    st.warning("比較表の作成に必要なデータ形式が見つかりませんでした。レポートのみ表示します。")
                    status.update(label="⚠️ 調査は完了しましたが表は作成できませんでした", state="complete")
            except Exception as e:
                st.error(f"解析エラー: {e}")

# ファイル名用にトピックを取得（もし無ければ "report" とする）
file_prefix = st.session_state.get('topic', 'report')

# レポートの表示
if 'report' in st.session_state and st.session_state['report']:
    st.markdown("---")
    st.subheader("📊 分析レポート")
    st.markdown(st.session_state['report'])
    
    # ★追加: レポートのダウンロードボタン
    st.download_button(
        label="📄 レポートをダウンロード (Text)",
        data=st.session_state['report'],
        file_name=f"{file_prefix}_report.md",
        mime="text/markdown"
    )

# 比較表の表示
if 'df' in st.session_state and st.session_state['df'] is not None:
    st.markdown("---")
    st.subheader("📋 競合比較表")
    st.dataframe(st.session_state['df'])
    
    # ★追加: CSVのダウンロードボタン
    csv = st.session_state['df'].to_csv(index=False).encode('utf-8')
    st.download_button(
        label="💾 比較データをダウンロード (CSV)",
        data=csv,
        file_name=f"{file_prefix}_competitors.csv",
        mime="text/csv"
    )