"""
apps/search/strategies.py
────────────────────────
SearchPool concreto do HomeMatch para busca de imóveis.
"""

from __future__ import annotations

from typing import Any, List

from framework.abstractions.abstract_search_pool import AbstractSearchPool
from apps.search.embeddings import EmbeddingService


class HomeMatchSearchPool(AbstractSearchPool):
    """
    Define quais atributos entram na busca natural e como os imóveis
    são ranqueados.
    """

    def getSearchableAttrs(self) -> List[str]:
        """
        Retorna os atributos pesquisáveis no domínio imobiliário.
        """
        return [
            "type",
            "property_purpose",
            "description",
            "address",
            "neighborhood",
            "city",
            "area",
            "price",
            "has_mobilia",
            "bedrooms",
            "bathrooms",
            "parking_spots",
            "living_room",
            "garden",
            "kitchen",
            "laundry_room",
            "pool",
            "office",
            "condo_gym",
            "condo_pool",
            "nearby_places",
            "subjective_attributes",
        ]

    def rank(self, query: str, posts: List[Any]) -> List[Any]:
        """
        Ordena os imóveis usando similaridade de embeddings.
        """
        query_embedding = EmbeddingService.embed_text(query)

        ranked_posts = []

        for post in posts:
            post_embedding = EmbeddingService.deserialize(
                getattr(post, "embedding", None)
            )

            score = EmbeddingService.cosine_similarity(
                query_embedding,
                post_embedding,
            )

            post.search_score = score
            ranked_posts.append(post)

        return sorted(
            ranked_posts,
            key=lambda post: post.search_score,
            reverse=True,
        )