# Project Trainer

AIがInBodyデータとユーザー情報を分析し、パーソナライズされたトレーニングメニューを自動生成するWebアプリケーションです。

## 機能

- **InBodyデータ入力** - 体重・筋肉量・体脂肪率・部位別骨格筋量をフォームで入力
- **InBody画像解析** - InBody結果シートの画像をアップロードすると、Gemini Vision APIで数値を自動抽出
- **AI分析レポート** - LangGraphエージェントが身体データを専門的に分析
- **トレーニングプラン生成** - 目標・環境・好みに応じた最適なメニューを作成
- **印刷対応** - 生成されたプランをそのまま印刷可能

## 技術スタック

### バックエンド
- Python 3.11 / Django 5.2 / Django REST Framework
- LangChain + LangGraph（AIエージェントパイプライン）
- Google Gemini（LLM / Vision API）
- ChromaDB（ベクトルデータベース）

### フロントエンド
- React 19 / Vite 7
- Material-UI (MUI) 7

### インフラ
- Docker / Docker Compose
- Nginx（リバースプロキシ）

## アーキテクチャ

```
ユーザー入力 → Django API → Orchestrator
                              ├── Analyzer（InBodyデータ分析）
                              │     └── ChromaDB（専門知識検索）
                              └── Planner（トレーニングプラン生成）
                                        ↓
                              レスポンス → React UI
```

## セットアップ（Docker）

### 前提条件
- Docker / Docker Compose
- Google API Key（Gemini API用）

### 1. リポジトリのクローン

```bash
git clone git@github.com:schwa-schwa/project-trainer.git
cd project-trainer
```

### 2. 環境変数の設定

プロジェクトルートに `.env` ファイルを作成:

```bash
cp .env.example .env
```

`.env` を編集して API Key を設定:

```env
GOOGLE_API_KEY=your_google_api_key_here
```

> **注意:** Docker Compose の `env_file` ディレクティブにより、`.env` の内容はコンテナの環境変数として注入されます。
> バックエンド内の `load_dotenv()` はローカル開発用のフォールバックです。

### 3. 起動

```bash
docker compose up --build
```

http://localhost でアプリケーションにアクセスできます。

### コンテナ構成

| サービス | ポート | 役割 |
|---------|-------|------|
| nginx | 80 | リバースプロキシ（`/api/` → backend, `/` → frontend） |
| backend | 8000（内部） | Django API サーバー |
| frontend | 5173（内部） | Vite 開発サーバー |

## セットアップ（ローカル開発）

Docker を使わずに開発する場合:

### バックエンド

```bash
# 依存関係のインストール
pip install -r requirements.txt

# .env はプロジェクトルートに配置（config.py が自動で読み込み）
# 起動
cd backend
python manage.py migrate
python manage.py runserver
```

### フロントエンド

```bash
cd frontend
npm install
npm run dev
```

> ローカル開発時、フロントエンドは `http://localhost:5173`、バックエンドは `http://localhost:8000` で動作します。
> CORS 設定により両ポートからのアクセスが許可されています。

## API エンドポイント

| メソッド | パス | 説明 |
|---------|------|------|
| `POST` | `/api/generate/` | トレーニングプラン生成 |
| `POST` | `/api/extract-inbody/` | InBody画像からデータ抽出 |
| `GET` | `/api/health/` | ヘルスチェック |
| `GET` | `/api/` | API情報 |

## プロジェクト構成

```
project_trainer/
├── backend/
│   ├── api/              # Django REST API（views, serializers）
│   ├── config/           # Django 設定（settings, urls）
│   ├── core/
│   │   ├── analyzer/     # InBody データ分析エージェント
│   │   │   └── knowledge/  # 専門知識ベース（Markdown）
│   │   ├── planner/      # トレーニングプラン生成エージェント
│   │   ├── orchestrator/ # Analyzer → Planner のパイプライン統合
│   │   └── common/       # 共通モジュール（LLM, ChromaDB, state）
│   ├── data/
│   │   └── chroma_db/    # ChromaDB データ（自動生成・git 管理外）
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/   # React UI コンポーネント
│   │   └── services/     # API 通信（axios）
│   └── Dockerfile
├── .env                  # 環境変数（git 管理外）
├── docker-compose.yml
├── nginx.conf
└── requirements.txt
```
