"""
examples/dating/strategies/search_pool.py
────────────────────────────────────────
SearchPool concreto para a instância Dating.
"""

from __future__ import annotations

from typing import Any, List

from framework.abstractions.abstract_search_pool import AbstractSearchPool


class DatingSearchPool(AbstractSearchPool):
    """
    Define atributos pesquisáveis e ranking para perfis de encontros.
    """

    def getSearchableAttrs(self) -> List[str]:
        return [
            "bio",
            "interests",
            "hobbies",
            "city",
            "lifestyle",
        ]

    def rank(self, query: str, posts: List[Any]) -> List[Any]:
        query_tokens = set(query.lower().split())

        for post in posts:
            searchable_text = " ".join(
                [
                    str(post.get("bio", "")),
                    " ".join(post.get("interests", [])),
                    " ".join(post.get("hobbies", [])),
                    str(post.get("city", "")),
                    str(post.get("lifestyle", "")),
                ]
            ).lower()

            post.search_score = len(
                query_tokens.intersection(set(searchable_text.split()))
            )

        return sorted(posts, key=lambda item: item.search_score, reverse=True)