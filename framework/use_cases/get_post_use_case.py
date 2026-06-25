"""
framework/use_cases/get_post_by_id_use_case.py
──────────────────────────────────────────────
Use case fixo do framework responsável por buscar uma postagem pelo ID.

Fluxo fixo:
  1. Recebe o ID da postagem
  2. Valida se o ID foi informado
  3. Solicita ao repositório da instância a busca da postagem
  4. Retorna a postagem encontrada

Ponto flexível usado:
  - AbstractPostRepository
"""

from __future__ import annotations

from typing import Any

from framework.abstract_post_repository import AbstractPostRepository


class GetPostByIdUseCase:
    """
    Caso de uso fixo para buscar uma postagem pelo identificador.

    O framework define que existe uma operação de busca por ID.
    A instância define como essa postagem será buscada no banco.
    """

    def __init__(self, post_repository: AbstractPostRepository) -> None:
        self.post_repository = post_repository

    def execute(self, *, post_id: Any) -> Any:
        """
        Busca uma postagem pelo ID.

        :param post_id: identificador da postagem
        :return: postagem encontrada
        """
        self._validate_input(post_id=post_id)

        post = self.post_repository.get_post_by_id(post_id)

        if post is None:
            raise ValueError("Postagem não encontrada.")

        return post

    def _validate_input(self, *, post_id: Any) -> None:
        """
        Valida os dados mínimos necessários para buscar uma postagem.
        """
        if post_id is None:
            raise ValueError("O ID da postagem é obrigatório.")
