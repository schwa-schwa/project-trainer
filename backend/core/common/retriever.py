import threading
from typing import List
from core.common.db_client import get_vectorstore

_retriever_lock = threading.Lock()


def search_knowledge(query: str, k: int = 3, fetch_k: int = 10, lambda_mult: float = 0.5) -> str:
    """
    ナレッジベースからMMR検索を実行し、フォーマット済みテキストを返す。

    Args:
        query: 検索クエリ
        k: 返す結果数
        fetch_k: MMRの候補数
        lambda_mult: MMRの多様性パラメータ（0=多様性重視, 1=類似度重視）
    """
    with _retriever_lock:
        vectorstore = get_vectorstore()
        retriever = vectorstore.as_retriever(
            search_type="mmr",
            search_kwargs={"k": k, "fetch_k": fetch_k, "lambda_mult": lambda_mult},
        )
        results = retriever.invoke(query)

    if not results:
        return f"「{query}」に関する専門知識は見つかりませんでした。"

    return "\n\n".join(
        f"【結果{i}】\n{doc.page_content}" for i, doc in enumerate(results, 1)
    )