"""
framework/use_cases/list_posts_use_case.py
─────────────────────────────────────────
Use case fixo do framework responsável pela listagem de postagens.

Fluxo fixo:
  1. Solicita ao repositório da instância a lista de postagens
  2. Retorna as postagens encontradas

Ponto flexível usado:
  - AbstractPostRepository
"""

from __future__ import annotations

from typing import Any, List

from framework.abstract_post_repository import AbstractPostRepository


class ListPostsUseCase:
    """
    Caso de uso fixo para listagem de postagens.

    O framework define que existe uma operação de listagem.
    A instância define como as postagens são buscadas e ordenadas.
    """

    def __init__(self, post_repository: AbstractPostRepository) -> None:
        self.post_repository = post_repository

    def execute(self) -> List[Any]:
        """
        Lista as postagens disponíveis da instância.

        :return: lista de postagens
        """
        return self.post_repository.list_posts()