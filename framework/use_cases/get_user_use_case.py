"""
framework/use_cases/get_user_by_email_use_case.py
────────────────────────────────────────────────
Use case fixo do framework responsável por buscar um usuário pelo e-mail.

Fluxo fixo:
  1. Recebe um e-mail
  2. Valida se o e-mail foi informado
  3. Normaliza o e-mail
  4. Solicita ao repositório da instância a busca do usuário
  5. Retorna o usuário encontrado

Ponto flexível usado:
  - AbstractUserRepository
"""

from __future__ import annotations

from typing import Any

from framework.abstract_user_repository import AbstractUserRepository


class GetUserByEmailUseCase:
    """
    Caso de uso fixo para buscar usuário por e-mail.

    O framework define o fluxo de busca.
    A instância define como o usuário será recuperado do banco.
    """

    def __init__(self, user_repository: AbstractUserRepository) -> None:
        self.user_repository = user_repository

    def execute(self, *, email: str) -> Any:
        """
        Busca um usuário pelo e-mail.

        :param email: e-mail do usuário
        :return: usuário encontrado
        """
        self._validate_input(email=email)

        normalized_email = self._normalize_email(email)

        user = self.user_repository.get_by_email(normalized_email)

        if user is None:
            raise ValueError("Usuário não encontrado.")

        return user

    def _validate_input(self, *, email: str) -> None:
        """
        Valida os dados mínimos necessários para buscar um usuário.
        """
        if not email or not email.strip():
            raise ValueError("O e-mail é obrigatório.")

    def _normalize_email(self, email: str) -> str:
        """
        Normaliza o e-mail antes da busca.
        """
        return email.strip().lower()