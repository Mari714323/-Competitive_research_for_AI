# 🚀 AI 起業アイデア壁打ちエージェント

起業アイデアや個人開発のネタを入力するだけで、AIエージェントチームが「市場調査」から「戦略立案」、さらには「要件定義・システム設計」までを一気通貫で行う支援ツールです。

## 概要

このアプリケーションは **Streamlit** と **CrewAI** (Google Gemini API) を使用して構築されています。
7人の専門家AIエージェントがチームを組み、あなたのアイデアを多角的に分析・具体化します。

## ✨ 主な機能

### 1. 徹底的な市場調査
- **🕵️ リサーチャー**: Web検索を行い、競合サービスや市場トレンドを調査します。
- **✍️ ライター**: 調査結果をわかりやすいレポートにまとめます。

### 2. 戦略とフィードバック（オプション）
- **♟️ 戦略コンサル**: SWOT分析（強み・弱み・機会・脅威）を行い、差別化戦略を提案します。
- **🏃‍♂️ 起業コーチ**: アイデア実現のための「最初の1ヶ月のアクションプラン」を提示します。
- **🗣️ 辛口ユーザー**: 想定ターゲットになりきり、忖度なしの本音フィードバックを行います。

### 3. 開発ドキュメント生成（オプション）
- **👩‍💻 プロダクトマネージャー (PdM)**: 必要な機能一覧、ユーザーストーリー、画面遷移などの「要件定義書」を作成します。
- **👨‍💻 テックリード**: 推奨技術スタック（言語・FW）、DB設計（ER図）、API設計などの「基本設計書」を作成します。

### 4. 便利なUI機能
- **詳細ヒアリングシート**: プロダクト名・ターゲット・特徴を入力することで分析精度を向上。
- **履歴キャッシュ機能**: 一度調査した内容はローカル(`history.json`)に保存され、2回目以降はAPI消費なしで高速表示。
- **レポートダウンロード**: 分析結果をMarkdown、競合リストをCSVでダウンロード可能。

## 📦 インストール方法

### 前提条件
- Python 3.10 以上
- Google Gemini API Key

### 手順

1. リポジトリをクローンします
   ```bash
   git clone [https://github.com/Mari714323/-Competitive_research_for_AI.git](https://github.com/Mari714323/-Competitive_research_for_AI.git)
   cd Competitive_research_for_AI
仮想環境を作成し、依存ライブラリをインストールします

Bash
python -m venv .venv
source .venv/bin/activate  # Windowsの場合: .venv\Scripts\activate
pip install -r requirements.txt
環境変数を設定します
.env ファイルを作成し、APIキーを記述してください。

Plaintext
GEMINI_API_KEY=your_api_key_here
🚀 使い方
アプリケーションを起動します

Bash
python -m streamlit run app.py
ブラウザが立ち上がるので、以下の項目を入力します

プロダクト名: 作りたいサービスの名前

ターゲット: 誰のどんな課題を解決するか

特徴・強み: 競合との違いや解決策

必要なオプション（戦略、コーチ、設計など）にチェックを入れ、「調査を開始する」をクリックします。

🛠️ 使用技術
Frontend: Streamlit

AI Framework: CrewAI

LLM: Google Gemini Pro

Tools: SerperDevTool (Google Search)

📂 ディレクトリ構成
ai-research-agent/
├── app.py              # アプリケーションのエントリーポイント
├── src/
│   ├── crew.py         # AIエージェントとタスクの定義
│   └── tools.py        # 検索ツールの定義
├── history.json        # 検索履歴のキャッシュ（git管理外）
├── requirements.txt    # 依存ライブラリ
└── README.md           # ドキュメント


