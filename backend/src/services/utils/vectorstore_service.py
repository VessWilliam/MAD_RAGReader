import hashlib
from typing import List

from langchain_community.document_loaders import DirectoryLoader, PyPDFLoader
from langchain_community.embeddings import FastEmbedEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core._api.deprecation import T
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from ..config import DATA_DIR, VECTORSTORE_PATH

INDEX_FILE = VECTORSTORE_PATH / "index.faiss"
HASH_FILE = VECTORSTORE_PATH / "data.hash"


class VectorStoreService:
    def load_or_build(self, embeddings: FastEmbedEmbeddings) -> FAISS:
        current_hash = self._compute_pdf_hash()
        if self._is_vectorstore_valid(current_hash):
            return self._load(embeddings)

        vectorstore = self._build(embeddings)
        HASH_FILE.write_text(current_hash)
        return vectorstore

    # -- public facing helpers --
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

    def _build(self, embedding: FastEmbedEmbeddings) -> FAISS:
        self._validate_data_dir()
        VECTORSTORE_PATH.mkdir(parents=True, exist_ok=True)
        documents = self._load_documents()
        chunks = self._split_documents(documents)
        vectorstore = FAISS.from_documents(chunks, embedding)
        vectorstore.save_local(str(VECTORSTORE_PATH))
        return vectorstore

    def _validate_data_dir(self) -> None:
        if not DATA_DIR.exists():
            raise FileNotFoundError(f"Data directory not found at {DATA_DIR}")
        if not list(DATA_DIR.glob("**/*.pdf")):
            raise FileNotFoundError(f"No PDF files found in {DATA_DIR}")

    # -- private helpers --
    def _load_documents(self) -> List[Document]:
        loader = DirectoryLoader(
            str(DATA_DIR),
            glob="**/*.pdf",
            loader_cls=PyPDFLoader,  # type: ignore[arg-type]
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

        hashresult = hashlib.md5()

        for f in files:
            hashresult.update(f.read_bytes())
        return hashresult.hexdigest()
