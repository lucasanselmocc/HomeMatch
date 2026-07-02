"""
framework/use_cases/search_posts_use_case.py
───────────────────────────────────────────
Use case fixo do framework responsável pela busca de postagens por linguagem natural.
"""

from __future__ import annotations

from typing import Any

from framework.abstractions.abstract_post_repository import AbstractPostRepository
from framework.abstractions.abstract_search_pool import AbstractSearchPool
from framework.search.nl_query_interpreter import NLQueryInterpreter


class SearchPostsUseCase:
    def __init__(self, post_repository, search_pool):
        self.post_repository = post_repository
        self.search_pool = search_pool

    def execute(self, *, query: str):
        if not query or not query.strip():
            raise ValueError("A consulta de busca é obrigatória.")

        posts = self.post_repository.list_posts()

        results = self.search_pool.rank(
            query=query.strip(),
            posts=posts,
        )

        self.search_pool.persist(results)

        return results