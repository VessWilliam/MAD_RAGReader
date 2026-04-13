import hashlib
from typing import List, Optional

from langchain_community.document_loaders import DirectoryLoader, PyPDFLoader
from langchain_community.embeddings import FastEmbedEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from ..config import DATA_DIR, VECTORSTORE_PATH

INDEX_FILE = VECTORSTORE_PATH / "index.faiss"
HASH_FILE = VECTORSTORE_PATH / "data.hash"


class VectorStoreService:
    def load_or_build(self, embeddings: FastEmbedEmbeddings) -> Optional[FAISS]:
        current_hash = self._compute_pdf_hash()
        if not current_hash:
            print("No PDFs found. Vectorstore not created.")
            return None

        if self._is_vectorstore_valid(current_hash):
            return self._load(embeddings)

        return self._build(embeddings, current_hash)

    # -- public helpers --
    def _is_vectorstore_valid(self, current_hash: str) -> bool:
        return (
            INDEX_FILE.exists()
            and HASH_FILE.exists()
            and HASH_FILE.read_text() == current_hash
        )

    def _load(self, embeddings: FastEmbedEmbeddings) -> FAISS:
        return FAISS.load_local(
            str(VECTORSTORE_PATH),
            embeddings=embeddings,
            allow_dangerous_deserialization=True,
        )

    def _build(self, embedding: FastEmbedEmbeddings, current_hash: str) -> FAISS:
        VECTORSTORE_PATH.mkdir(parents=True, exist_ok=True)

        documents = self._load_documents()
        if not documents:
            print("[WARN] : No documents loaded.")
            return None

        chunks = self._split_documents(documents)

        vectorstore = FAISS.from_documents(chunks, embedding)
        vectorstore.save_local(str(VECTORSTORE_PATH))

        HASH_FILE.write_text(current_hash)

        return vectorstore

    # -- private helpers --
    def _load_documents(self) -> List[Document]:
        if not DATA_DIR.exists():
            return []

        loader = DirectoryLoader(
            str(DATA_DIR),
            glob="**/*.pdf",
            loader_cls=PyPDFLoader,
            use_multithreading=True,
        )
        return loader.load()

    def _split_documents(self, documents: List[Document]) -> List[Document]:
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=600,
            chunk_overlap=100,
            separators=["\n\n", "\n", ".", " ", ""],
        )

        chunks = splitter.split_documents(documents)
        return chunks

    def _compute_pdf_hash(self) -> str:
        if not DATA_DIR.exists():
            return ""

        files = sorted(DATA_DIR.glob("**/*.pdf"))
        if not files:
            return ""

        hashresult = hashlib.md5()

        for f in files:
            hashresult.update(f.read_bytes())

        return hashresult.hexdigest()