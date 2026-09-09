import os
from typing import Any, Dict, List, Optional

from src.features.rag.domain.hybrid_retrieval import HybridRetrievalResult
from src.features.rag.infrastructure.embedding_retriever import EmbeddingRetriever
from src.features.rag.infrastructure.hybrid_retriever import HybridRetriever
from src.features.rag.infrastructure.lexical_retriever import LexicalRetriever


class HybridRetrievalUseCase:
    """Application boundary for hybrid retrieval without answer generation."""

    def __init__(
        self,
        base_dir: str,
        retriever: Optional[HybridRetriever] = None,
    ):
        if retriever:
            self.retriever = retriever
        else:
            processed_dir = os.path.join(base_dir, "data", "processed")
            store_dir = os.path.join(base_dir, "data", "embeddings", "legal_chunks")
            
            lexical = LexicalRetriever(processed_dir)
            embedding = EmbeddingRetriever(store_dir)
            self.retriever = HybridRetriever(lexical, embedding)

    def execute(
        self,
        query: str,
        top_k: int = 5,
        jurisdiction: Optional[str] = None,
        domain: Optional[str] = None,
    ) -> Dict[str, Any]:
        results: List[HybridRetrievalResult] = self.retriever.search(
            query=query,
            top_k=top_k,
            jurisdiction=jurisdiction,
            domain=domain,
        )
        
        # Check if we have meaningful results (abstention logic placeholder)
        # We don't apply a hardcoded threshold to filter them out, 
        # but if no candidates match filters, we return empty.
        
        return {
            "query": query,
            "top_k": top_k,
            "jurisdiction_filter": jurisdiction,
            "domain_filter": domain,
            "retrieval_method": "hybrid_rrf",
            "embedding_model": self.retriever.embedding.model_name,
            "llm_generation": False,
            "results": [result.to_dict() for result in results],
        }
