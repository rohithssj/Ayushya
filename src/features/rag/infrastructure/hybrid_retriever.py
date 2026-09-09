import re
from typing import Any, Dict, List, Optional, Set

from src.features.rag.domain.hybrid_retrieval import HybridRetrievalResult
from src.features.rag.infrastructure.embedding_retriever import EmbeddingRetriever
from src.features.rag.infrastructure.lexical_retriever import LexicalRetriever


class HybridRetriever:
    """Combines lexical and embedding retrieval using Reciprocal Rank Fusion (RRF)."""

    def __init__(self, lexical: LexicalRetriever, embedding: EmbeddingRetriever):
        self.lexical = lexical
        self.embedding = embedding
        self.rrf_k = 60  # Standard constant for RRF

    def search(
        self,
        query: str,
        top_k: int = 5,
        jurisdiction: Optional[str] = None,
        domain: Optional[str] = None,
        pool_size: int = 20,
    ) -> List[HybridRetrievalResult]:
        if not query.strip():
            raise ValueError("Query must contain at least one non-whitespace character")
        if top_k < 1:
            raise ValueError("top_k must be at least 1")

        # Get candidates from both retrievers
        lexical_results = self.lexical.search(
            query=query, top_k=pool_size, jurisdiction=jurisdiction, domain=domain
        )
        embedding_results = self.embedding.search(
            query=query, top_k=pool_size, jurisdiction=jurisdiction, domain=domain
        )

        # Build rank maps
        lexical_ranks = {
            res.chunk.get("chunk_id"): (rank + 1, res.matched_terms, res.score)
            for rank, res in enumerate(lexical_results)
        }
        max_lexical_score = max((res.score for res in lexical_results), default=0.0)
        embedding_ranks = {
            res.chunk.get("chunk_id"): rank + 1
            for rank, res in enumerate(embedding_results)
        }

        # Combine unique chunks
        unique_chunks: Dict[str, Dict[str, Any]] = {}
        for res in lexical_results:
            chunk_id = res.chunk.get("chunk_id")
            if chunk_id:
                unique_chunks[chunk_id] = res.chunk
                
        for res in embedding_results:
            chunk_id = res.chunk.get("chunk_id")
            if chunk_id and chunk_id not in unique_chunks:
                unique_chunks[chunk_id] = res.chunk

        # Calculate RRF scores with quality boosts/penalties
        scored_results: List[HybridRetrievalResult] = []
        for chunk_id, chunk in unique_chunks.items():
            lex_rank, matched_terms, lexical_score = lexical_ranks.get(
                chunk_id, (pool_size + 1, tuple(), 0.0)
            )
            emb_rank = embedding_ranks.get(chunk_id, pool_size + 1)

            lexical_confidence = (
                lexical_score / max_lexical_score if max_lexical_score else 0.0
            )
            lexical_weight = (
                1.0 + lexical_confidence + lexical_confidence**2
                if lexical_score
                else 0.0
            )
            rrf_score = (lexical_weight / (self.rrf_k + lex_rank)) + (
                1.0 / (self.rrf_k + emb_rank)
            )
            
            # Apply penalties/boosts based on text quality
            final_score = rrf_score * self._text_quality_multiplier(chunk)
            
            scored_results.append(
                HybridRetrievalResult(
                    chunk=chunk,
                    hybrid_score=final_score,
                    lexical_rank=lex_rank,
                    semantic_rank=emb_rank,
                    matched_terms=matched_terms,
                )
            )

        # Sort by final score descending
        scored_results.sort(key=lambda x: (-x.hybrid_score, x.chunk.get("chunk_id", "")))
        
        return scored_results[:top_k]

    @staticmethod
    def _text_quality_multiplier(chunk: Dict[str, Any]) -> float:
        """Penalize obvious TOC/headings and boost substantive legal text."""
        text = str(chunk.get("text", ""))
        lines = text.splitlines()
        
        # Remove metadata header if present to analyze body
        body = "\n".join(lines[1:]) if lines and lines[0].startswith("[") else text
        words = re.findall(r"[A-Za-z]{2,}", body)
        
        if len(words) < 10:
            return 0.5  # Heavy penalty for extremely short chunks
            
        has_toc_dots = bool(re.search(r"(?:\.\.\.|…{2,})", body))
        has_legal_provision = bool(
            re.search(r"\b(?:shall|must|may|means|provided|prohibited|patent|approval|requirement)\b", body, re.IGNORECASE)
        )
        
        multiplier = 1.0
        if has_toc_dots and not has_legal_provision:
            multiplier *= 0.7  # Penalize TOC
            
        if has_legal_provision:
            multiplier *= 1.2  # Boost substantive provisions
            
        return multiplier
