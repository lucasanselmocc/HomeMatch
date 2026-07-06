"""
framework/use_cases/search_post_use_case.py
──────────────────────────────────────────
Use case fixo do framework responsável pela busca de postagens
por linguagem natural.
"""

from __future__ import annotations

from typing import Any, List

from framework.abstractions.abstract_post_repository import AbstractPostRepository
from framework.abstractions.abstract_search_pool import AbstractSearchPool
from framework.abstractions.abstract_query_interpreter import AbstractQueryInterpreter


class SearchPostsUseCase:
    """
    Caso de uso fixo para busca de postagens por linguagem natural.

    O framework controla o fluxo geral:
      - valida a query;
      - interpreta a consulta, se houver interpretador configurado;
      - busca postagens candidatas;
      - delega o ranking ao SearchPool da instância;
      - persiste o resultado, se necessário.
    """

    def __init__(
        self,
        post_repository: AbstractPostRepository,
        search_pool: AbstractSearchPool,
        query_interpreter: AbstractQueryInterpreter | None = None,
    ) -> None:
        self.post_repository = post_repository
        self.search_pool = search_pool
        self.query_interpreter = query_interpreter

    def execute(self, *, query: str) -> List[Any]:
        """
        Busca postagens relevantes para uma consulta textual.
        """
        self._validate_input(query=query)

        normalized_query = query.strip()

        criteria = {}

        if self.query_interpreter is not None:
            criteria = self.query_interpreter.interpret(normalized_query)

        candidate_posts = self.post_repository.filter_posts(criteria)

        ranked_posts = self.search_pool.rank(
            query=normalized_query,
            posts=candidate_posts,
        )

        self.search_pool.persist(ranked_posts)

        return ranked_posts

    def _validate_input(self, *, query: str) -> None:
        """
        Valida os dados mínimos necessários para realizar uma busca.
        """
        if not query or not query.strip():
            raise ValueError("A consulta de busca é obrigatória.")