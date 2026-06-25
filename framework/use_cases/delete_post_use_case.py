"""
framework/use_cases/delete_post_use_case.py
──────────────────────────────────────────
Use case fixo do framework responsável pela exclusão de postagens.

Fluxo fixo:
  1. Recebe uma postagem existente
  2. Valida se a postagem foi informada
  3. Solicita ao repositório da instância a remoção da postagem
  4. Retorna o resultado da operação

Ponto flexível usado:
  - AbstractPostRepository
"""

from __future__ import annotations

from typing import Any

from framework.abstract_post_repository import AbstractPostRepository


class DeletePostUseCase:
    """
    Caso de uso fixo para exclusão de postagens.

    O framework controla o fluxo geral de exclusão.
    A instância define como a postagem será removida ou desativada.
    """

    def __init__(self, post_repository: AbstractPostRepository) -> None:
        self.post_repository = post_repository

    def execute(self, *, post: Any) -> None:
        """
        Remove ou desativa uma postagem existente.

        :param post: postagem que será removida/desativada
        """
        self._validate_input(post=post)

        self.post_repository.delete_post(post)

    def _validate_input(self, *, post: Any) -> None:
        """
        Valida os dados mínimos necessários para excluir uma postagem.
        """
        if post is None:
            raise ValueError("A postagem é obrigatória.")