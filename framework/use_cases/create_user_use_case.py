"""
framework/use_cases/create_user_use_case.py
──────────────────────────────────────────
Use case fixo do framework responsável pela criação de usuários.
"""

from __future__ import annotations

from typing import Any

from framework.abstract_user_repository import AbstractUserRepository


class CreateUserUseCase:
    """
    Caso de uso fixo para criação de usuários.

    O framework controla a regra geral de criação:
      - validar os dados mínimos;
      - verificar e-mail duplicado;
      - delegar a persistência para o repositório concreto.
    """

    def __init__(self, user_repository: AbstractUserRepository) -> None:
        self.user_repository = user_repository

    def execute(
        self,
        *,
        email: str,
        name: str,
        user_type: str,
        password: str,
    ) -> Any:
        """
        Cria um novo usuário.
        """
        self._validate_input(
            email=email,
            name=name,
            user_type=user_type,
            password=password,
        )

        normalized_email = self._normalize_email(email)

        if self.user_repository.email_exists(normalized_email):
            raise ValueError("Já existe um usuário cadastrado com este e-mail.")

        return self.user_repository.create_user(
            email=normalized_email,
            name=name.strip(),
            user_type=user_type.strip(),
            password=password,
        )

    def _validate_input(
        self,
        *,
        email: str,
        name: str,
        user_type: str,
        password: str,
    ) -> None:
        """
        Valida os dados mínimos necessários para criar um usuário.
        """
        if not email or not email.strip():
            raise ValueError("O e-mail é obrigatório.")

        if not name or not name.strip():
            raise ValueError("O nome é obrigatório.")

        if not user_type or not user_type.strip():
            raise ValueError("O tipo de usuário é obrigatório.")

        if not password:
            raise ValueError("A senha é obrigatória.")

    def _normalize_email(self, email: str) -> str:
        """
        Normaliza o e-mail antes de consultar ou persistir.
        """
        return email.strip().lower()
