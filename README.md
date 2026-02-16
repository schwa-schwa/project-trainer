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

## セットアップ

### 前提条件
- Docker / Docker Compose
- Google API Key（Gemini API用）

### 1. 環境変数の設定

プロジェクトルートに`.env`ファイルを作成:

```env
GOOGLE_API_KEY=your_google_api_key_here
```

### 2. Docker Composeで起動

```bash
docker compose up --build
```

アプリケーションが http://localhost で利用可能になります。

### ローカル開発（Docker不使用）

**バックエンド:**

```bash
pip install -r requirements.txt
cd backend
python manage.py runserver
```

**フロントエンド:**

```bash
cd frontend
npm install
npm run dev
```

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
│   ├── api/            # Django REST API
│   ├── config/         # Django設定
│   ├── core/
│   │   ├── analyzer/   # InBodyデータ分析エージェント
│   │   ├── planner/    # トレーニングプラン生成エージェント
│   │   ├── orchestrator/ # エージェント統合
│   │   └── common/     # 共通ユーティリティ（LLM, state, retriever）
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/ # React UIコンポーネント
│   │   └── services/   # API通信
│   └── Dockerfile
├── docker-compose.yml
├── nginx.conf
└── requirements.txt
```
