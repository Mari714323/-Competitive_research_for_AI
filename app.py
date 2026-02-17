import streamlit as st
import pandas as pd
from src.crew import (
    researcher, writer, strategist, coach, persona, pdm, architect,
    research_task, analysis_task, strategy_task, coach_task, persona_task, requirements_task, design_task
)
from src.utils import (
    load_history_data, save_history_data, clean_topic_name, 
    extract_json_from_text, split_report_by_agent
)
from crewai import Crew, Process

# --- ページ設定 ---
st.set_page_config(page_title="AI 競合調査エージェント", layout="wide")

st.title("🤖 AI 起業アイデア壁打ちエージェント")
st.markdown("あなたの起業アイデアを入力してください。AIチームが市場調査から戦略立案まで行います。")

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

# --- 設定エリア ---
st.markdown("---")
st.subheader("⚙️ 調査オプション")

opt_col1, opt_col2 = st.columns(2)

with opt_col1:
    st.markdown("**追加エージェント**")
    use_strategy = st.checkbox("🕵️ 戦略コンサル（SWOT分析）", value=True)
    use_coach = st.checkbox("🏃‍♂️ 起業コーチ（アクションプラン）", value=False)
    use_persona = st.checkbox("🗣️ 辛口ユーザー（フィードバック）", value=False)
    use_design = st.checkbox("💻 システム設計（仕様書・設計書）", value=True)

with opt_col2:
    st.markdown("**検索設定**")
    search_limit = st.slider("検索上限数", 1, 10, 5, help="AIが参考にするWebサイトの数です。多いほど時間はかかりますが情報量が増えます。")
    force_fetch = st.checkbox("強制的にWeb検索を行う", value=False, help="チェックを入れると、過去の履歴を使わずに最新の情報を取得し直します。")

st.markdown("") # 余白

# --- 実行ボタン ---
if st.button("🚀 調査を開始する", type="primary"):
    if not product_name:
        st.warning("まずは「プロダクト名」を入力してください。")
    else:
        # トピック名の安全化
        safe_topic_name = clean_topic_name(product_name)
        st.session_state['topic'] = safe_topic_name
        
        # 1. 履歴の確認
        history = load_history_data()
        
        if topic in history and not force_fetch:
            st.info(f"📜 「{product_name}」の過去の調査履歴が見つかりました。APIを使わずに表示します。")
            cached_data = history[topic]
            st.session_state['report'] = cached_data['report']
            
            if cached_data['df_data']:
                st.session_state['df'] = pd.DataFrame(cached_data['df_data'])
            else:
                st.session_state['df'] = None
        
        # 2. AI実行
        else:
            st.session_state['df'] = None
            st.session_state['report'] = None

            with st.status("🚀 AIエージェントチームが調査中...") as status:
                # チーム編成
                my_agents = [researcher, writer]
                my_tasks = [research_task, analysis_task]
                
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

                if use_design:
                    my_agents.append(pdm)
                    my_tasks.append(requirements_task)
                    my_agents.append(architect)
                    my_tasks.append(design_task)
                    st.write("💻 開発チーム（PdM・テックリード）が参加しました")

                # タスク記述の更新
                research_task.description = f"以下のプロダクト案について市場調査を行い、競合サービスをリストアップしてください。\n\n{topic}\n\n検索結果が英語であっても、報告は必ず日本語で行ってください。"
                analysis_task.description = """
                レポートを作成してください。
                最後に、調査した競合サービス（3〜5つ）と、ユーザーのアイデア（自分のプロダクト）を比較するためのJSONデータを出力してください。
                各サービスを以下の2軸で1〜10点で採点してください：
                - functionality: 機能の豊富さ（1:単機能 〜 10:多機能・オールインワン）
                - usability: 手軽さ・初心者への優しさ（1:難しい・専門的 〜 10:簡単・直感的）
                
                JSON形式:
                [
                    {"name": "競合A", "url": "...", "features": "...", "functionality": 7, "usability": 8, "type": "competitor"},
                    {"name": "自分のプロダクト", "url": "-", "features": "...", "functionality": 5, "usability": 9, "type": "self"}
                ]
                必ずこのJSONブロックのみを最後に出力してください。
                """

                # 実行
                crew = Crew(
                    agents=my_agents,
                    tasks=my_tasks,
                    process=Process.sequential
                )
                
                result = crew.kickoff(inputs={'topic': topic})
                
                # 結果の結合
                full_report = ""
                for task_output in result.tasks_output:
                    agent_role = getattr(task_output, 'agent', '担当エージェント')
                    full_report += f"## 👤 {agent_role} の報告\n\n"
                    full_report += str(task_output) + "\n\n---\n\n"
                
                st.session_state['report'] = full_report
                
                # JSONデータの抽出（utils関数を使用）
                df_data = None
                
                # analysis_taskの結果からJSONを探す（もしanalysis_taskがあれば）
                # ※タスクリストの順番が変わっても大丈夫なように、output.raw全体から探す簡易的な方法をとります
                extracted_data = extract_json_from_text(full_report)
                
                if extracted_data:
                    # ★修正: データが「リスト」じゃなかったら、リストに入れてあげる（重要！）
                    if isinstance(extracted_data, list):
                         df_data = extracted_data
                    else:
                         df_data = [extracted_data]
                    
                    st.session_state['df'] = pd.DataFrame(df_data)
                    status.update(label="✅ 全工程完了！レポートができました", state="complete")
                else:
                    st.session_state['df'] = None
                    status.update(label="⚠️ 分析完了（比較表データなし）", state="complete")

                # 履歴に保存
                save_history_data(topic, full_report, df_data)


# --- 結果表示エリア ---
file_prefix = st.session_state.get('topic', 'report')

if 'report' in st.session_state and st.session_state['report']:
    st.markdown("---")
    st.subheader("📊 分析レポート")
    
    report_text = st.session_state['report']
    
    # utils関数を使って分割
    roles, contents = split_report_by_agent(report_text)
    
    if roles:
        tabs = st.tabs(roles)
        for i, tab in enumerate(tabs):
            with tab:
                st.markdown(contents[i])
    else:
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
    
    # データフレームの表示
    st.dataframe(st.session_state['df'])
    
    # ポジショニングマップの表示
    # データに点数カラムがあるか確認
    df = st.session_state['df']
    if 'functionality' in df.columns and 'usability' in df.columns:
        st.subheader("🗺️ ポジショニングマップ")
        st.info("縦軸：機能の豊富さ（高いほど多機能） / 横軸：手軽さ（右に行くほど簡単）")
        
        # 散布図の作成
        st.scatter_chart(
            df,
            x='usability',
            y='functionality',
            color='name', # 色でサービスを区別
            size=100,     # ドットのサイズ
        )
    
    # CSVダウンロードボタン（元の位置のまま）
    csv = st.session_state['df'].to_csv(index=False).encode('utf-8')
    st.download_button(
        label="💾 比較データをダウンロード (CSV)",
        data=csv,
        file_name=f"{file_prefix}_competitors.csv",
        mime="text/csv"
    )
