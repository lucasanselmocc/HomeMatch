"""
examples/makeup/strategies/search_pool.py
────────────────────────────────────────
SearchPool concreto para a instância Makeup.
"""

from __future__ import annotations

from typing import Any, List

from framework.abstractions.abstract_search_pool import AbstractSearchPool


class MakeupSearchPool(AbstractSearchPool):
    """
    Define atributos pesquisáveis e ranking para produtos de maquiagem.
    """

    def getSearchableAttrs(self) -> List[str]:
        return [
            "name",
            "brand",
            "category",
            "description",
            "skin_type",
            "finish",
            "color",
        ]

    def rank(self, query: str, posts: List[Any]) -> List[Any]:
        query_tokens = set(query.lower().split())

        for post in posts:
            searchable_text = " ".join(
                [
                    str(getattr(post, "name", "")),
                    str(getattr(post, "brand", "")),
                    str(getattr(post, "category", "")),
                    str(getattr(post, "description", "")),
                    str(getattr(post, "skin_type", "")),
                    str(getattr(post, "finish", "")),
                    str(getattr(post, "color", "")),
                ]
            ).lower()

            post.search_score = len(
                query_tokens.intersection(set(searchable_text.split()))
            )

        return sorted(posts, key=lambda item: item.search_score, reverse=True)

    def persist(self, results):
        pass