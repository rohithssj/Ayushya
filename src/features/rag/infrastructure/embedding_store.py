import json
from pathlib import Path
from typing import Any, Dict, List

import numpy as np


_STORE_CACHE: Dict[Path, tuple[np.ndarray, List[Dict[str, Any]], str]] = {}


class EmbeddingStore:
    """File-backed local storage for normalized vectors and chunk metadata."""

    def __init__(self, store_dir: str):
        self.store_dir = Path(store_dir)
        self.vectors_path = self.store_dir / "vectors.npy"
        self.metadata_path = self.store_dir / "metadata.json"

    def save(
        self,
        vectors: np.ndarray,
        chunks: List[Dict[str, Any]],
        model_name: str,
    ) -> None:
        if len(vectors) != len(chunks):
            raise ValueError("The number of vectors must match the number of chunks")
        if vectors.ndim != 2:
            raise ValueError("Embedding vectors must be a two-dimensional array")

        self.store_dir.mkdir(parents=True, exist_ok=True)
        np.save(self.vectors_path, vectors.astype(np.float32))
        payload = {
            "model_name": model_name,
            "vector_count": len(chunks),
            "dimensions": int(vectors.shape[1]),
            "chunks": chunks,
        }
        with self.metadata_path.open("w", encoding="utf-8") as file:
            json.dump(payload, file, indent=2, ensure_ascii=False)
        _STORE_CACHE.pop(self.store_dir.resolve(), None)

    def load(self) -> tuple[np.ndarray, List[Dict[str, Any]], str]:
        resolved_path = self.store_dir.resolve()
        if resolved_path in _STORE_CACHE:
            return _STORE_CACHE[resolved_path]

        if not self.vectors_path.exists() or not self.metadata_path.exists():
            raise FileNotFoundError(
                f"Embedding store is incomplete: expected {self.vectors_path} and {self.metadata_path}"
            )
        vectors = np.load(self.vectors_path, allow_pickle=False)
        with self.metadata_path.open("r", encoding="utf-8") as file:
            payload = json.load(file)
        chunks = payload.get("chunks")
        model_name = payload.get("model_name")
        if not isinstance(chunks, list) or not isinstance(model_name, str):
            raise ValueError("Embedding metadata is missing chunks or model_name")
        if vectors.shape[0] != len(chunks):
            raise ValueError("Embedding vectors and metadata contain different counts")

        result = (vectors, chunks, model_name)
        _STORE_CACHE[resolved_path] = result
        return result