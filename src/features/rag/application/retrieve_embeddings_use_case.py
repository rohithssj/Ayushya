import os
from typing import Any, Dict, List, Optional

from src.features.rag.domain.embedding_retrieval import EmbeddingRetrievalResult
from src.features.rag.infrastructure.embedding_retriever import EmbeddingRetriever


class RetrieveEmbeddingsUseCase:
    """Application boundary for embedding retrieval without answer generation."""

    def __init__(self, base_dir: str, retriever: Optional[EmbeddingRetriever] = None):
        store_dir = os.path.join(base_dir, "data", "embeddings", "legal_chunks")
        self.retriever = retriever or EmbeddingRetriever(store_dir)

    def execute(
        self,
        query: str,
        top_k: int = 5,
        jurisdiction: Optional[str] = None,
        domain: Optional[str] = None,
    ) -> Dict[str, Any]:
        results: List[EmbeddingRetrievalResult] = self.retriever.search(
            query=query,
            top_k=top_k,
            jurisdiction=jurisdiction,
            domain=domain,
        )
        return {
            "query": query,
            "top_k": top_k,
            "jurisdiction_filter": jurisdiction,
            "domain_filter": domain,
            "retrieval_method": "sentence_transformers_cosine",
            "embedding_model": self.retriever.model_name,
            "llm_generation": False,
            "results": [result.to_dict() for result in results],
        }