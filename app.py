import streamlit as st
import pandas as pd
from crewai import Crew, Process
from src.crew import (
    researcher, writer, strategist, coach, persona,
    research_task, analysis_task, strategy_task, coach_task, persona_task
)
import io
import json
import os
import re

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
    
    # 検索のコツを表示
    with st.expander("💡 検索のヒント"):
        st.markdown("""
        - **単語で入力**: 「〜について教えて」などの文章は不要です。
        - **具体的に**: 「AI」より「営業支援AIツール」のように絞り込むと精度が上がります。
        - **迷ったら**: 「誰のための」「何をするツール」かを書くとAIが理解しやすくなります。
        """)
        
    search_limit = st.slider("検索上限数", 1, 10, 5)

    st.markdown("---")
    st.subheader("追加オプション")
    use_strategy = st.checkbox("戦略立案（SWOT分析）", value=True)
    use_coach = st.checkbox("アクションプラン提案", value=False)
    use_persona = st.checkbox("ユーザーフィードバック", value=False)
    
    st.markdown("---")
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
                
        # 2. 履歴がないならAIを実行
        else:
            # 画面を真っさらに
            st.session_state['df'] = None
            st.session_state['report'] = None

            with st.status("🚀 AIエージェントがチームで調査中...") as status:
                # 1. 基本メンバーとタスク
                my_agents = [researcher, writer]
                my_tasks = [research_task, analysis_task]
                
                # 2. オプションに応じてメンバーを追加
                if use_strategy:
                    my_agents.append(strategist)
                    my_tasks.append(strategy_task)
                    st.write("🕵️ 戦略コンサルタントが参加しました")
                
                if use_coach:
                    my_agents.append(coach)
                    my_tasks.append(coach_task)
                    st.write("🏃‍♂️ スタートアップ・コーチが参加しました")

                if use_persona:
                    my_agents.append(persona)
                    my_tasks.append(persona_task)
                    st.write("🗣️ 辛口ユーザーが参加しました")

                # タスク記述のセット（ここは変わりません）
                research_task.description = f"「{topic}」の市場を調査し、競合サービスをリストアップしてください。"
                analysis_task.description = "レポートを作成し、最後に必ず [{\"サービス名\": \"...\", \"URL\": \"...\", \"特徴\": \"...\"}] 形式のJSONを含めてください。"
                
                # 3. 動的に作ったチームで実行
                crew = Crew(
                    agents=my_agents,
                    tasks=my_tasks,
                    process=Process.sequential
                )
                
                result = crew.kickoff(inputs={'topic': topic})
                
                # 全タスクの結果を結合して、豪華なレポートを作成する
                full_report = ""
                
                # result.tasks_output には、実行された全タスクの結果リストが入っています
                for task_output in result.tasks_output:
                    # 担当したエージェント名を取得（不明な場合は汎用名）
                    agent_role = getattr(task_output, 'agent', '担当エージェント')
                    
                    # 見出しと内容をレポートに追加
                    full_report += f"## 👤 {agent_role} の報告\n\n"
                    full_report += str(task_output) + "\n\n---\n\n"
                
                # 結合した結果を保存
                st.session_state['report'] = full_report
                
                # JSON抽出ロジック（ここは前回と同じですが、念のため再掲）
                try:
                    # analysis_taskの結果を取得（タスクが増減するので名前で探すのが安全ですが、簡易的に分析タスクは必ず2番目にあると仮定）
                    if analysis_task.output:
                        analysis_result = str(analysis_task.output.raw)
                    else:
                        analysis_result = full_report
                except:
                    analysis_result = full_report
            
                # JSONデータの抽出
                df_data = None
                try:
                    import re
                    json_match = re.search(r'\[.*\]', analysis_result, re.DOTALL)
                    if json_match:
                        df_data = json.loads(json_match.group())
                        st.session_state['df'] = pd.DataFrame(df_data)
                        status.update(label="✅ 全工程完了！SWOT分析レポートができました", state="complete")
                    else:
                        st.session_state['df'] = None
                        status.update(label="⚠️ 分析は完了しましたが、比較表のデータが見つかりませんでした", state="complete")
                    
                    # ★ここで定義済みの swot_report を使う
                    save_history_data(topic, full_report, df_data)
                    
                except Exception as e:
                    st.error(f"解析エラー: {e}")

# （※ここより下の表示・ダウンロード部分は昨日のままでOKです）
# ファイル名用にトピックを取得（もし無ければ "report" とする）
file_prefix = st.session_state.get('topic', 'report')

# レポートの表示
file_prefix = st.session_state.get('topic', 'report')

# レポートの表示（タブ化して見やすく！）
if 'report' in st.session_state and st.session_state['report']:
    st.markdown("---")
    st.subheader("📊 分析レポート")
    
    report_text = st.session_state['report']
    
    # 正規表現を使って、「## 👤 {名前} の報告」という見出しごとにテキストを分割する
    # splitの結果は [前置き, 名前1, 内容1, 名前2, 内容2...] というリストになります
    # ※もしエージェント名変更等で分割がうまくいかない場合に備え、分割できなかった時の処理も入れています
    try:
        sections = re.split(r'## 👤 (.*?) の報告\n\n', report_text)
        
        # うまく分割できたらタブ表示にする
        if len(sections) > 1:
            # リストの奇数番目が「名前」、偶数番目が「内容」になります
            roles = sections[1::2]
            contents = sections[2::2]
            
            # エージェントの人数分だけタブを作成
            tabs = st.tabs(roles)
            
            # 各タブに中身を書き込む
            for i, tab in enumerate(tabs):
                with tab:
                    st.markdown(contents[i])
        else:
            # 分割できなかった場合はそのまま表示
            st.markdown(report_text)
            
    except Exception as e:
        # 万が一のエラー時はそのまま表示
        st.markdown(report_text)
    
    # ダウンロードボタンはタブの外（共通）に置く
    st.download_button(
        label="📄 レポート全文をダウンロード (Text)",
        data=report_text,
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