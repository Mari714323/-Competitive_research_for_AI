import streamlit as st
import pandas as pd
from src.crew import (
    researcher, writer, strategist, coach, persona,
    research_task, analysis_task, strategy_task, coach_task, persona_task
)
from crewai import Crew, Process
import json
import os
import re

# --- ページ設定 ---
st.set_page_config(page_title="AI 競合調査エージェント", layout="wide")

st.title("🤖 AI 起業アイデア壁打ちエージェント")
st.markdown("あなたの起業アイデアを入力してください。AIチームが市場調査から戦略立案まで行います。")

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
        "df_data": df_data
    }
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=4)

# --- メイン画面：ヒアリングシート ---
st.markdown("### 📝 アイデア・ヒアリングシート")
st.info("詳しい情報を入力するほど、AIのアドバイスの精度が上がります！")

col1, col2 = st.columns(2)

with col1:
    product_name = st.text_input("🔹 プロダクト・サービス名", placeholder="例：ADHD向けタスク管理アプリ")

    st.markdown("**🔹 ターゲット（誰の課題？）**")
    st.caption("ヒント：具体的な属性（フリーランス、主婦など）や、抱えている悩み（締め切りが守れない、献立が思いつかない）を書きましょう")
    target_audience = st.text_area("ターゲット", placeholder="例：締め切り管理が苦手なフリーランス。着手するまでのハードルが高く、いつもギリギリになって自己嫌悪に陥っている人。", height=100, label_visibility="collapsed")

with col2:
    st.markdown("**🔹 主な特徴・独自の強み**")
    st.caption("ヒント：既存の競合と何が違うのか？ どうやって課題を解決するのか？（AI活用、低価格、コミュニティ機能など）")
    main_features = st.text_area("特徴", placeholder="例：AIがタスクを細分化してハードルを下げる。着手できただけで褒めてくれる機能。月額500円。", height=100, label_visibility="collapsed")
    
    st.markdown("**🔹 あなたの現状（任意）**")
    st.caption("ヒント：個人開発、予算ゼロ、技術力、開発期間など、考慮してほしい事情があれば")
    context_info = st.text_area("現状", placeholder="例：エンジニア1名で開発。予算はほぼゼロなので広告は打てない。", height=100, label_visibility="collapsed")

# 入力情報を結合して「トピック」を作る
if product_name:
    topic = f"""
    【プロダクト名】{product_name}
    【ターゲット】{target_audience}
    【特徴・強み】{main_features}
    【開発者の現状】{context_info}
    """
else:
    topic = ""

# --- 設定エリア（メイン画面に移動） ---
st.markdown("---")
st.subheader("⚙️ 調査オプション")

opt_col1, opt_col2 = st.columns(2)

with opt_col1:
    st.markdown("**追加エージェント**")
    use_strategy = st.checkbox("🕵️ 戦略コンサル（SWOT分析）", value=True)
    use_coach = st.checkbox("🏃‍♂️ 起業コーチ（アクションプラン）", value=False)
    use_persona = st.checkbox("🗣️ 辛口ユーザー（フィードバック）", value=False)

with opt_col2:
    st.markdown("**検索設定**")
    search_limit = st.slider("検索上限数", 1, 10, 5, help="AIが参考にするWebサイトの数です。多いほど時間はかかりますが情報量が増えます。")
    force_fetch = st.checkbox("強制的にWeb検索を行う", value=False, help="チェックを入れると、過去の履歴を使わずに最新の情報を取得し直します。")

st.markdown("") # 少し余白

# --- 実行ボタン ---
if st.button("🚀 調査を開始する", type="primary"):
    if not product_name:
        st.warning("まずは「プロダクト名」を入力してください。")
    else:
        # ファイル名用にトピックを保存（ファイル名に使えない文字を除去）
        safe_topic_name = re.sub(r'[\\/:*?"<>|]+', '', product_name)
        st.session_state['topic'] = safe_topic_name
        
        # 1. 履歴の確認
        history = load_history_data()
        
        # 履歴があり、かつ「強制検索」がOFFなら履歴を使う
        if topic in history and not force_fetch:
            st.info(f"📜 「{product_name}」の過去の調査履歴が見つかりました。APIを使わずに表示します。")
            cached_data = history[topic]
            st.session_state['report'] = cached_data['report']
            
            if cached_data['df_data']:
                st.session_state['df'] = pd.DataFrame(cached_data['df_data'])
            else:
                st.session_state['df'] = None
        
        # 2. 履歴がないならAIを実行
        else:
            st.session_state['df'] = None
            st.session_state['report'] = None

            with st.status("🚀 AIエージェントチームが調査中...") as status:
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

                # タスク記述のセット（トピックには詳細情報が全部入っています）
                research_task.description = f"以下のプロダクト案について市場調査を行い、競合サービスをリストアップしてください。\n\n{topic}\n\n検索結果が英語であっても、報告は必ず日本語で行ってください。"
                analysis_task.description = "レポートを作成し、最後に必ず [{\"サービス名\": \"...\", \"URL\": \"...\", \"特徴\": \"...\"}] 形式のJSONを含めてください。"
                
                # 3. チーム実行
                crew = Crew(
                    agents=my_agents,
                    tasks=my_tasks,
                    process=Process.sequential
                )
                
                result = crew.kickoff(inputs={'topic': topic})
                
                # 全タスクの結果を結合
                full_report = ""
                for task_output in result.tasks_output:
                    agent_role = getattr(task_output, 'agent', '担当エージェント')
                    full_report += f"## 👤 {agent_role} の報告\n\n"
                    full_report += str(task_output) + "\n\n---\n\n"
                
                st.session_state['report'] = full_report
                
                # JSONデータの抽出
                try:
                    if analysis_task.output:
                        analysis_result = str(analysis_task.output.raw)
                    else:
                        analysis_result = full_report
                except:
                    analysis_result = full_report
                
                df_data = None
                try:
                    json_match = re.search(r'\[.*\]', analysis_result, re.DOTALL)
                    if json_match:
                        df_data = json.loads(json_match.group())
                        st.session_state['df'] = pd.DataFrame(df_data)
                        status.update(label="✅ 全工程完了！レポートができました", state="complete")
                    else:
                        st.session_state['df'] = None
                        status.update(label="⚠️ 分析完了（比較表データなし）", state="complete")
                    
                    # 履歴に保存
                    save_history_data(topic, full_report, df_data)
                    
                except Exception as e:
                    st.error(f"解析エラー: {e}")


# --- 結果表示エリア（タブ表示） ---
file_prefix = st.session_state.get('topic', 'report')

if 'report' in st.session_state and st.session_state['report']:
    st.markdown("---")
    st.subheader("📊 分析レポート")
    
    report_text = st.session_state['report']
    
    try:
        sections = re.split(r'## 👤 (.*?) の報告\n\n', report_text)
        
        if len(sections) > 1:
            roles = sections[1::2]
            contents = sections[2::2]
            
            tabs = st.tabs(roles)
            for i, tab in enumerate(tabs):
                with tab:
                    st.markdown(contents[i])
        else:
            st.markdown(report_text)
            
    except Exception as e:
        st.markdown(report_text)
    
    st.download_button(
        label="📄 レポート全文をダウンロード (Text)",
        data=report_text,
        file_name=f"{file_prefix}_report.md",
        mime="text/markdown"
    )

if 'df' in st.session_state and st.session_state['df'] is not None:
    st.markdown("---")
    st.subheader("📋 競合比較表")
    st.dataframe(st.session_state['df'])
    
    csv = st.session_state['df'].to_csv(index=False).encode('utf-8')
    st.download_button(
        label="💾 比較データをダウンロード (CSV)",
        data=csv,
        file_name=f"{file_prefix}_competitors.csv",
        mime="text/csv"
    )