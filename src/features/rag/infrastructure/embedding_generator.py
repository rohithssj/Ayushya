import json
from pathlib import Path
from typing import Any, Dict, List

from src.features.rag.domain.embedding_retrieval import embedding_text
from src.features.rag.infrastructure.embedding_store import EmbeddingStore


class EmbeddingGenerator:
    """Generate local sentence-transformer embeddings for processed chunks."""

    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        self.model_name = model_name

    def generate(self, processed_dir: str, store_dir: str, batch_size: int = 64) -> Dict[str, Any]:
        chunks = self._load_chunks(processed_dir)
        texts = [embedding_text(chunk) for chunk in chunks]

        try:
            from sentence_transformers import SentenceTransformer
        except ImportError as error:
            raise RuntimeError(
                "sentence-transformers is required; install it before generating embeddings"
            ) from error

        model = SentenceTransformer(self.model_name)
        vectors = model.encode(
            texts,
            batch_size=batch_size,
            show_progress_bar=True,
            convert_to_numpy=True,
            normalize_embeddings=True,
        )
        EmbeddingStore(store_dir).save(vectors, chunks, self.model_name)
        return {
            "model_name": self.model_name,
            "chunks_embedded": len(chunks),
            "dimensions": int(vectors.shape[1]),
            "store_dir": store_dir,
        }

    @staticmethod
    def _load_chunks(processed_dir: str) -> List[Dict[str, Any]]:
        directory = Path(processed_dir)
        chunks: List[Dict[str, Any]] = []
        for path in sorted(directory.glob("*_chunks.json")):
            with path.open("r", encoding="utf-8") as file:
                loaded = json.load(file)
            if not isinstance(loaded, list):
                raise ValueError(f"Expected a JSON list in processed chunk file: {path}")
            chunks.extend(loaded)
        if not chunks:
            raise ValueError(f"No processed chunks found in: {directory}")
        return chunks