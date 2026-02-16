import threading
from pathlib import Path
from langchain_chroma import Chroma
from core.common.config import BACKEND_DIR
from core.common.llm import get_embeddings

_vectorstore_cache = None
_vectorstore_lock = threading.Lock()

DB_PATH = BACKEND_DIR / "data" / "chroma_db"
KNOWLEDGE_FILE = BACKEND_DIR / "core" / "analyzer" / "knowledge" / "expert_knowledge.md"


def _ensure_documents_loaded(vectorstore: Chroma) -> None:
    """DBが空の場合、ナレッジベースからドキュメントを追加する"""
    existing_docs = vectorstore.get()
    if len(existing_docs["ids"]) > 0:
        return

    print("   - DBが空のため、ドキュメントを追加中...")

    if not KNOWLEDGE_FILE.exists():
        raise FileNotFoundError(f"ナレッジベースファイルが見つかりません: {KNOWLEDGE_FILE}")

    from langchain_community.document_loaders import TextLoader
    from langchain_text_splitters import MarkdownHeaderTextSplitter, RecursiveCharacterTextSplitter

    loader = TextLoader(str(KNOWLEDGE_FILE), encoding="utf-8")
    docs = loader.load()

    markdown_splitter = MarkdownHeaderTextSplitter(
        headers_to_split_on=[("#", "Header 1"), ("##", "Header 2"), ("###", "Header 3")],
        strip_headers=False,
    )
    split_docs = markdown_splitter.split_text(docs[0].page_content)

    recursive_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=20,
        separators=["\n\n", "\n", "、", "。", ""],
    )
    all_splits = recursive_splitter.split_documents(split_docs)

    print(f"   - {len(all_splits)}件のドキュメントをインデックス化")
    vectorstore.add_documents(all_splits)
    print("   - DBにドキュメントを追加しました")


def get_vectorstore(collection_name: str = "inbody_knowledge") -> Chroma:
    """スレッドセーフなシングルトンChroma VectorStoreを取得（初回はドキュメント自動登録）"""
    global _vectorstore_cache

    with _vectorstore_lock:
        if _vectorstore_cache is not None:
            return _vectorstore_cache

        embeddings = get_embeddings()
        DB_PATH.mkdir(parents=True, exist_ok=True)

        _vectorstore_cache = Chroma(
            collection_name=collection_name,
            embedding_function=embeddings,
            persist_directory=str(DB_PATH),
        )

        _ensure_documents_loaded(_vectorstore_cache)

        return _vectorstore_cache