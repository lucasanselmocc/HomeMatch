"""
framework/use_cases/update_user_use_case.py
──────────────────────────────────────────
Use case fixo do framework responsável pela atualização de usuários.

Fluxo fixo:
  1. Recebe um usuário existente
  2. Recebe os dados atualizados
  3. Valida os dados mínimos
  4. Aplica as alterações no usuário
  5. Salva usando o repositório da instância
  6. Retorna o usuário atualizado

Ponto flexível usado:
  - AbstractUserRepository
"""

from __future__ import annotations

from typing import Any

from framework.abstract_user_repository import AbstractUserRepository


class UpdateUserUseCase:
    """
    Caso de uso fixo para atualização de usuários.

    O framework controla o fluxo geral de atualização.
    A instância define como o usuário será persistido.
    """

    def __init__(self, user_repository: AbstractUserRepository) -> None:
        self.user_repository = user_repository

    def execute(self, *, user: Any, validated_data: dict) -> Any:
        """
        Atualiza um usuário existente.

        :param user: usuário que será atualizado
        :param validated_data: dados já validados pela camada de entrada
        :return: usuário atualizado
        """
        self._validate_input(
            user=user,
            validated_data=validated_data,
        )

        for field, value in validated_data.items():
            setattr(user, field, value)

        return self.user_repository.save_user(user)

    def _validate_input(self, *, user: Any, validated_data: dict) -> None:
        """
        Valida os dados mínimos necessários para atualizar um usuário.
        """
        if user is None:
            raise ValueError("O usuário é obrigatório.")

        if validated_data is None:
            raise ValueError("Os dados do usuário são obrigatórios.")

        if not isinstance(validated_data, dict):
            raise TypeError("Os dados do usuário devem estar em formato de dicionário.")