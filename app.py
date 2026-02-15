import streamlit as st
import pandas as pd
from crewai import Crew, Process
from main import researcher, writer, research_task, analysis_task # main.pyから流用
import io
import json
import os

# --- 履歴ファイルの保存先 ---
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
        "df_data": df_data # DataFrameではなく辞書リストとして保存
    }
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=4)

# --- ページ設定 ---
st.set_page_config(page_title="AI 競合調査エージェント", layout="wide")

st.title("🤖 AI 競合調査エージェント")
st.markdown("調査したい製品やサービス名を入力すると、AIがネットから情報を集めて分析レポートを作成します。")

# --- サイドバー：設定 ---
with st.sidebar:
    st.header("設定")
    topic = st.text_input("調査対象の業種・製品", placeholder="例：個人向けタスク管理アプリ")
    search_limit = st.slider("検索上限数", 1, 10, 5)
    # ★追加: キャッシュを使うかどうかのスイッチ
    force_fetch = st.checkbox("強制的にWeb検索を行う", value=False, help="チェックを入れると履歴を無視してAPIを使用します")

# --- メイン画面：実行ボタン ---
if st.button("調査を開始する", type="primary"):
    if not topic:
        st.warning("調査対象を入力してください。")
    else:
        # ファイル名用にトピックを保存
        st.session_state['topic'] = topic
        
        # 履歴の確認
        history = load_history_data()
        
        # 【判定】履歴があり、かつ「強制検索」がOFFなら履歴を使う
        if topic in history and not force_fetch:
            st.info(f"📜 「{topic}」の過去の調査履歴が見つかりました。APIを使わずに表示します。")
            
            # データの復元
            cached_data = history[topic]
            st.session_state['report'] = cached_data['report']
            
            # リスト形式のデータをDataFrameに戻す
            if cached_data['df_data']:
                st.session_state['df'] = pd.DataFrame(cached_data['df_data'])
            else:
                st.session_state['df'] = None
                
        else:
            # 履歴がない、または強制検索の場合はAIを実行
            with st.status("🚀 AIエージェントが調査中...") as status:
                # 前回同様のAI実行処理...
                research_task.description = f"「{topic}」の市場を調査し、競合サービスをリストアップしてください。"
                analysis_task.description = "レポートを作成し、最後に必ず [{\"サービス名\": \"...\", \"URL\": \"...\", \"特徴\": \"...\"}] 形式のJSONを含めてください。"
                
                crew = Crew(agents=[researcher, writer], tasks=[research_task, analysis_task])
                result = crew.kickoff(inputs={'topic': topic})
                
                report_text = str(result.raw)
                st.session_state['report'] = report_text
                
                # JSONデータの抽出と保存処理
                df_data = None # 保存用
                try:
                    import re
                    json_match = re.search(r'\[.*\]', report_text, re.DOTALL)
                    if json_match:
                        df_data = json.loads(json_match.group()) # リスト形式
                        st.session_state['df'] = pd.DataFrame(df_data)
                        status.update(label="✅ 調査完了！", state="complete")
                    else:
                        st.session_state['df'] = None
                        st.warning("比較表データが見つかりませんでした。")
                        status.update(label="⚠️ 表作成スキップ", state="complete")
                    
                    # ★ここで履歴に保存！
                    save_history_data(topic, report_text, df_data)
                    
                except Exception as e:
                    st.error(f"解析エラー: {e}")

# （※ここより下の表示・ダウンロード部分は昨日のままでOKです）
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