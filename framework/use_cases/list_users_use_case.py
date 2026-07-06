"""
framework/use_cases/list_users_use_case.py
─────────────────────────────────────────
Use case fixo do framework responsável pela listagem de usuários.
"""

from __future__ import annotations

from typing import Any

from framework.abstractions.abstract_user_repository import AbstractUserRepository


class ListUsersUseCase:
    """
    Caso de uso fixo para listagem de usuários.

    O framework controla o fluxo geral de listagem,
    delegando a recuperação dos dados ao repositório concreto.
    """

    def __init__(self, user_repository: AbstractUserRepository) -> None:
        self.user_repository = user_repository

    def execute(self) -> list[Any]:
        """
        Lista todos os usuários cadastrados.
        """
        return self.user_repository.list_users()
