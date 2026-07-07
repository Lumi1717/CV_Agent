import logging
import os
from dataclasses import dataclass
from typing import List, Optional, Sequence, Tuple

import numpy as np
from langchain_core.documents import Document
from sklearn.feature_extraction.text import TfidfVectorizer

logger = logging.getLogger(__name__)


def _cosine_sim_matrix(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    a_norm = a / (np.linalg.norm(a, axis=1, keepdims=True) + 1e-12)
    b_norm = b / (np.linalg.norm(b, axis=1, keepdims=True) + 1e-12)
    return a_norm @ b_norm.T


@dataclass(frozen=True)
class RetrievedDoc:
    doc: Document
    score: float
    source: str


class TfidfRetriever:
    def __init__(self, documents: Sequence[Document]):
        self._documents = list(documents)
        texts = [d.page_content for d in self._documents]
        self._vectorizer = TfidfVectorizer(stop_words="english")
        self._matrix = self._vectorizer.fit_transform(texts)

    def retrieve(self, query: str, k: int) -> List[RetrievedDoc]:
        q = self._vectorizer.transform([query])
        scores = (self._matrix @ q.T).toarray().reshape(-1)
        if scores.size == 0:
            return []
        top_idx = np.argsort(-scores)[:k]
        return [
            RetrievedDoc(doc=self._documents[i], score=float(scores[i]), source="tfidf")
            for i in top_idx
            if scores[i] > 0
        ]


class SentenceTransformerRetriever:
    def __init__(self, documents: Sequence[Document], model_name: str):
        self._documents = list(documents)
        self._model_name = model_name
        from sentence_transformers import SentenceTransformer

        self._model = SentenceTransformer(model_name)
        self._doc_vecs = self._model.encode(
            [d.page_content for d in self._documents],
            normalize_embeddings=True,
            show_progress_bar=False,
        )
        self._doc_vecs = np.asarray(self._doc_vecs, dtype=np.float32)

    def retrieve(self, query: str, k: int) -> List[RetrievedDoc]:
        q_vec = self._model.encode(
            [query], normalize_embeddings=True, show_progress_bar=False
        )
        q_vec = np.asarray(q_vec, dtype=np.float32)
        sims = (self._doc_vecs @ q_vec.T).reshape(-1)
        top_idx = np.argsort(-sims)[:k]
        return [
            RetrievedDoc(
                doc=self._documents[i], score=float(sims[i]), source="semantic"
            )
            for i in top_idx
        ]


class HybridRetriever:
    def __init__(
        self,
        documents: Sequence[Document],
        k_tfidf: int = 10,
        k_semantic: int = 10,
        semantic_model_name: Optional[str] = None,
    ):
        self._documents = list(documents)
        self._tfidf = TfidfRetriever(self._documents)
        self._k_tfidf = k_tfidf
        self._k_semantic = k_semantic

        self._semantic: Optional[SentenceTransformerRetriever] = None
        if semantic_model_name:
            try:
                self._semantic = SentenceTransformerRetriever(
                    self._documents, semantic_model_name
                )
            except Exception:
                logger.exception(
                    "Failed to init SentenceTransformerRetriever; falling back to TF-IDF only"
                )
                self._semantic = None

    def retrieve(self, query: str, k: int) -> List[Document]:
        tfidf_hits = self._tfidf.retrieve(query, k=self._k_tfidf)
        semantic_hits: List[RetrievedDoc] = []
        if self._semantic is not None:
            semantic_hits = self._semantic.retrieve(query, k=self._k_semantic)

        # Reciprocal rank fusion (stable, simple)
        scores = {}

        def add_rrf(hits: List[RetrievedDoc], weight: float):
            for rank, hit in enumerate(hits, start=1):
                doc_id = id(hit.doc)
                scores.setdefault(doc_id, (hit.doc, 0.0))
                doc, cur = scores[doc_id]
                scores[doc_id] = (doc, cur + weight * (1.0 / (60 + rank)))

        add_rrf(tfidf_hits, weight=1.0)
        add_rrf(semantic_hits, weight=1.0)

        ranked = sorted(scores.values(), key=lambda x: x[1], reverse=True)
        return [doc for doc, _score in ranked[:k]]


def build_retriever(documents: Sequence[Document]) -> HybridRetriever:
    mode = os.getenv("RETRIEVER_MODE", "hybrid").strip().lower()
    semantic_model = os.getenv(
        "SEMANTIC_MODEL_NAME", "sentence-transformers/all-MiniLM-L6-v2"
    ).strip()

    if mode == "tfidf":
        return HybridRetriever(documents, semantic_model_name=None)

    return HybridRetriever(documents, semantic_model_name=semantic_model)
