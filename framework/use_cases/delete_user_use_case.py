"""
framework/use_cases/delete_user_use_case.py
──────────────────────────────────────────
Use case fixo do framework responsável pela remoção de usuários.
"""

from __future__ import annotations

from typing import Any

from framework.abstractions.abstract_user_repository import AbstractUserRepository


class DeleteUserUseCase:
    """
    Caso de uso fixo para remoção de usuários.

    O framework controla o fluxo geral de remoção:
      - validar se o usuário foi informado;
      - delegar a exclusão para o repositório concreto.
    """

    def __init__(self, user_repository: AbstractUserRepository) -> None:
        self.user_repository = user_repository

    def execute(self, *, user: Any) -> None:
        """
        Remove um usuário existente.
        """
        self._validate_input(user=user)

        self.user_repository.delete_user(user)

    def _validate_input(self, *, user: Any) -> None:
        """
        Valida os dados mínimos necessários para remover um usuário.
        """
        if user is None:
            raise ValueError("O usuário é obrigatório.")
