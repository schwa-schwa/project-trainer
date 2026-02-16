from langchain_core.tools import tool
from core.common.retriever import search_knowledge


@tool
def training_retriever_tool(query: str) -> str:
    """
    トレーニング関連の専門知識を検索するツール。

    【検索可能なカテゴリ (v3.1)】
    - 体型別戦略: 代謝特性、栄養戦略、有酸素運動ガイド
    - 種目検索: 「家でできる脚トレ」「ダンベルの背中種目」「初心者向け定番」
    - リスク管理: 関節リスク、代謝リスク、ホルモンリスク
    - 進行モデル: 初級(線形)〜上級(ピリオダイゼーション)
    - その他: リカバリー、サプリメント、左右差

    Args:
        query: 検索クエリ
            例: "週3回 初級者 全身法 リカバリー プロテイン"

    Returns:
        str: 検索結果のテキスト
    """
    return search_knowledge(query, k=4, fetch_k=12)


@tool
def risk_modification_tool(risk_factors: str) -> str:
    """
    リスク要因に応じた種目変更・代替案を検索するツール。

    【対応リスク】
    - 腰痛: デッドリフトの代替、コア強化
    - 膝の問題: スクワットの代替、レッグプレス
    - 肩の問題: オーバーヘッドプレスの代替、ローテーターカフ強化

    Args:
        risk_factors: リスク要因（カンマ区切りで複数可）
            例: "膝痛, 腰痛"

    Returns:
        str: リスク対策の検索結果
    """
    return search_knowledge(f"リスク 対策 代替種目 {risk_factors}", k=3, fetch_k=8, lambda_mult=0.6)