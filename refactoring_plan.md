# Refactoring Plan: Trainer Agent Project

本プロジェクトを可読性・保守性の高い構成にするためのリファクタリング計画です。

## 1. 現状の課題 (Current Issues)
1.  **インポートパスのハック**: 各 `main.py` で `sys.path.insert` を行っているため、IDEで補完が効きづらく、移動やデプロイに弱い。
2.  **構成の重複**: `get_llm` や `ChromaDB` の初期化コードが各ノードに散在している。
3.  **命名規則**: `analyzer_node/analyzer_node.py` のようにフォルダ名とファイル名が冗長。
4.  **設定ファイルの分散**: `.env` がサブディレクトリにあり、プロジェクト全体で管理しづらい。

## 2. 推奨ディレクトリ構成 (Proposed Structure)
「**srcレイアウト**」を採用し、パッケージを明確に分離します。共通処理は `common` モジュールに集約します。

```text
trainer_project/
├── .env                    # [移動] 環境変数をルートで一元管理
├── requirements.txt        # 依存ライブラリ一覧
├── main.py                 # [新設] 統合エントリーポイント (各モードを起動可能)
├── src/                    # ソースコードディレクトリ
│   ├── __init__.py
│   ├── common/             # [新設] 共通モジュール
│   │   ├── __init__.py
│   │   ├── config.py       # 環境変数・設定ロード
│   │   ├── llm.py          # get_llm, Embeddings初期化 (共通化)
│   │   ├── db_client.py    # ChromaDB接続ロジック (共通化)
│   │   └── state.py        # 共通State定義 (OrchestratorStateなど)
│   │
│   ├── analyzer/           # 旧 analyzer_node
│   │   ├── __init__.py
│   │   ├── graph.py        # 旧 analyzer_node.py (グラフ定義)
│   │   ├── tools.py        # 旧 rag_retriever.py (ツール定義)
│   │   └── knowledge/      # 知識ファイル
│   │       └── expert_knowledge.md
│   │
│   ├── planner/            # 旧 planner_node
│   │   ├── __init__.py
│   │   ├── graph.py        # 旧 planner_node.py
│   │   └── tools.py        # 旧 rag_retriever.py
│   │
│   └── orchestrator/       # 旧 orchestrator
│       ├── __init__.py
│       └── graph.py        # 旧 orchestrator.py
│
└── data/                   # [新設] 永続化データの保存先
    └── chroma_db/          # ベクトルDB (gitignore対象)
```

## 3. リファクタリング手順 (Step-by-Step)

### Phase 1: 基盤整備
1.  ルートディレクトリに `.env` を移動。
2.  `src/common` ディレクトリを作成し、`config.py` (設定読み込み), `llm.py` (LLM初期化) を実装。
3.  `sys.path` ハックなしで動作するルート `main.py` を作成。

### Phase 2: コード移行と共通化
4.  `analyzer_node` -> `src/analyzer` へ移動・リネーム。
    - `get_llm` などを `src.common.llm` からインポートするように変更。
5.  `planner_node` -> `src/planner` へ移動・リネーム。
    - 同様に共通モジュールを使用。
6.  `orchestrator` -> `src/orchestrator` へ移動。

### Phase 3: クリーンアップ
7.  各ディレクトリの `main.py` (テスト実行用) を削除、またはルートの `main.py` のサブコマンドとして統合。
8.  不要になった `sys.path.insert` を全削除。
9.  `black` や `isort` などのフォーマッターでコードスタイルを統一。

## 4. 期待される効果
- **可読性**: 構造が標準的になり、どこに何があるか予測しやすくなる。
- **保守性**: LLMのモデル変更やDB設定変更が1ファイル (`src/common/**`) の修正で済む。
- **開発効率**: IDEのインポート補完が正確に機能するようになる。
