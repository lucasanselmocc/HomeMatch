"""
framework/search/embedding_service.py
────────────────────────────────────
Serviço fixo do framework para geração e comparação de embeddings.
"""

from __future__ import annotations

import hashlib
import json
import math
import re
import unicodedata

from django.conf import settings

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None


LOCAL_EMBEDDING_DIMENSIONS = 256


class EmbeddingService:
    """
    Serviço genérico para transformar texto em embedding e comparar vetores.
    """

    @staticmethod
    def embed_text(text: str) -> list[float]:
        text = (text or "").strip()

        if not text:
            return []

        if OpenAI is not None and getattr(settings, "AI_API_KEY", None):
            try:
                client = OpenAI(
                    base_url=getattr(settings, "AI_API_BASE_URL", None),
                    api_key=settings.AI_API_KEY,
                )

                response = client.embeddings.create(
                    model=getattr(
                        settings,
                        "SEARCH_EMBEDDING_MODEL",
                        "text-embedding-004",
                    ),
                    input=text,
                )

                return [float(value) for value in response.data[0].embedding]

            except Exception:
                pass

        return EmbeddingService._local_embedding(text)

    @staticmethod
    def serialize(embedding: list[float]) -> str:
        return json.dumps(embedding or [], separators=(",", ":"))

    @staticmethod
    def deserialize(raw_embedding) -> list[float]:
        if not raw_embedding:
            return []

        if isinstance(raw_embedding, list):
            return [float(value) for value in raw_embedding]

        try:
            parsed = json.loads(raw_embedding)
        except (TypeError, ValueError):
            return []

        if not isinstance(parsed, list):
            return []

        return [float(value) for value in parsed]

    @staticmethod
    def cosine_similarity(left: list[float], right: list[float]) -> float:
        if not left or not right or len(left) != len(right):
            return 0.0

        dot = sum(a * b for a, b in zip(left, right))
        left_norm = math.sqrt(sum(a * a for a in left))
        right_norm = math.sqrt(sum(b * b for b in right))

        if not left_norm or not right_norm:
            return 0.0

        return dot / (left_norm * right_norm)

    @staticmethod
    def _local_embedding(text: str) -> list[float]:
        vector = [0.0] * LOCAL_EMBEDDING_DIMENSIONS
        tokens = re.findall(r"\w+", EmbeddingService._normalize_text(text))

        for token in tokens:
            digest = hashlib.sha256(token.encode("utf-8")).digest()
            index = int.from_bytes(digest[:4], "big") % LOCAL_EMBEDDING_DIMENSIONS
            sign = 1.0 if digest[4] % 2 == 0 else -1.0
            vector[index] += sign

        norm = math.sqrt(sum(value * value for value in vector))

        if not norm:
            return []

        return [value / norm for value in vector]

    @staticmethod
    def _normalize_text(text: str) -> str:
        normalized = unicodedata.normalize("NFKD", text.lower())
        return "".join(
            char for char in normalized if not unicodedata.combining(char)
        )