from __future__ import annotations

import os
from dataclasses import dataclass
from typing import List, Sequence

import numpy as np
from backend.ai.features.client import client

DEFAULT_EMBEDDING_MODEL = os.getenv('SUPPLYBOT_EMBEDDING_MODEL', 'google/gemini-embedding-2')


@dataclass(frozen=True)
class CloudEmbeddingModel:
    """API-backed embedding model for semantic search and persistence."""

    model: str = DEFAULT_EMBEDDING_MODEL

    def embed(self, text: str) -> np.ndarray:
        response = client.embeddings.create(model=self.model, input=text)
        return np.asarray(response.data[0].embedding, dtype=np.float32)

    def embed_many(self, texts: Sequence[str]) -> List[np.ndarray]:
        text_list = list(texts)
        if not text_list:
            return []

        response = client.embeddings.create(model=self.model, input=text_list)
        return [np.asarray(item.embedding, dtype=np.float32) for item in response.data]


HashEmbeddingModel = CloudEmbeddingModel


def cosine_similarity(left: Sequence[float], right: Sequence[float]) -> float:
    left_vector = np.asarray(left, dtype=np.float32)
    right_vector = np.asarray(right, dtype=np.float32)

    if left_vector.shape != right_vector.shape:
        raise ValueError("Embedding vectors must share the same shape")

    left_norm = float(np.linalg.norm(left_vector))
    right_norm = float(np.linalg.norm(right_vector))
    if not left_norm or not right_norm:
        return 0.0

    return float(np.dot(left_vector, right_vector) / (left_norm * right_norm))


def text_from_fields(*parts: object) -> str:
    return " ".join(str(part).strip() for part in parts if part not in (None, "")).strip()


def embedding_payload(vector: np.ndarray) -> List[float]:
    return [float(value) for value in vector.tolist()]
