import os
from typing import Any, Dict, List, Optional

from src.features.rag.domain.retrieval import RetrievalResult
from src.features.rag.infrastructure.lexical_retriever import LexicalRetriever


class RetrieveChunksUseCase:
    """Application boundary for retrieval without answer generation."""

    def __init__(self, base_dir: str, retriever: Optional[LexicalRetriever] = None):
        processed_dir = os.path.join(base_dir, "data", "processed")
        self.retriever = retriever or LexicalRetriever(processed_dir)

    def execute(
        self,
        query: str,
        top_k: int = 5,
        jurisdiction: Optional[str] = None,
        domain: Optional[str] = None,
    ) -> Dict[str, Any]:
        results: List[RetrievalResult] = self.retriever.search(
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
            "retrieval_method": "tfidf_cosine_lexical",
            "llm_generation": False,
            "results": [result.to_dict() for result in results],
        }