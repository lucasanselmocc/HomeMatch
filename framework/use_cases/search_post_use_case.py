"""
framework/use_cases/search_posts_use_case.py
───────────────────────────────────────────
Use case fixo do framework responsável pela busca de postagens por linguagem natural.

Fluxo fixo:
  1. Recebe uma consulta textual do usuário
  2. Busca as postagens candidatas
  3. Usa o SearchPool da instância para ranquear os resultados
  4. Persiste o resultado da busca, se a instância desejar
  5. Retorna as postagens ordenadas

Pontos flexíveis usados:
  - AbstractPostRepository
  - AbstractSearchPool
"""

from __future__ import annotations

from typing import Any, List

from framework.abstract_post_repository import AbstractPostRepository
from framework.abstract_search_pool import AbstractSearchPool


class SearchPostsUseCase:
    """
    Caso de uso fixo para busca de postagens por linguagem natural.

    O framework controla o fluxo geral da busca.
    A instância define:
      - quais atributos entram na busca;
      - como os resultados são ranqueados;
      - se os resultados serão persistidos ou não.
    """

    def __init__(
        self,
        post_repository: AbstractPostRepository,
        search_pool: AbstractSearchPool,
    ) -> None:
        self.post_repository = post_repository
        self.search_pool = search_pool

    def execute(self, *, query: str) -> List[Any]:
        """
        Busca postagens relevantes para uma consulta textual.

        :param query: consulta em linguagem natural feita pelo usuário
        :return: lista de postagens ordenadas por relevância
        """
        self._validate_input(query=query)

        candidate_posts = self.post_repository.list_posts()

        ranked_posts = self.search_pool.rank(
            query=query.strip(),
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