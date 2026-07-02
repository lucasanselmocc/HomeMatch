"""
framework/services/user_service.py
─────────────────────────────────
Service fixo do framework responsável por agrupar os casos de uso
relacionados ao gerenciamento de usuários.
"""

from __future__ import annotations

from typing import Any

from framework.use_cases.create_user_use_case import CreateUserUseCase
from framework.use_cases.delete_user_use_case import DeleteUserUseCase
from framework.use_cases.get_user_use_case import GetUserByEmailUseCase
from framework.use_cases.list_users_use_case import ListUsersUseCase
from framework.use_cases.update_user_use_case import UpdateUserUseCase


class UserService:
    """
    Service responsável pelo gerenciamento de usuários.

    Esta classe agrupa os casos de uso relacionados aos usuários,
    expondo uma API mais simples para a aplicação que utiliza
    o framework.
    """

    def __init__(
        self,
        create_user_use_case: CreateUserUseCase,
        get_user_use_case: GetUserByEmailUseCase,
        update_user_use_case: UpdateUserUseCase,
        delete_user_use_case: DeleteUserUseCase,
        list_users_use_case: ListUsersUseCase,
    ) -> None:
        """
        Inicializa o service com os casos de uso necessários.
        """
        self.create_user_use_case = create_user_use_case
        self.get_user_by_email_use_case = get_user_use_case
        self.update_user_use_case = update_user_use_case
        self.delete_user_use_case = delete_user_use_case
        self.list_users_use_case = list_users_use_case

    def create_user(
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
        return self.create_user_use_case.execute(
            email=email,
            name=name,
            user_type=user_type,
            password=password,
        )

    def get_user_by_email(self, *, email: str) -> Any:
        """
        Recupera um usuário pelo e-mail.
        """
        return self.get_user_by_email_use_case.execute(email=email)

    def update_user(self, *, user: Any, validated_data: dict) -> Any:
        """
        Atualiza os dados de um usuário.
        """
        return self.update_user_use_case.execute(
            user=user,
            validated_data=validated_data,
        )

    def delete_user(self, *, user: Any) -> None:
        """
        Remove um usuário existente.
        """
        return self.delete_user_use_case.execute(user=user)

    def list_users(self) -> list[Any]:
        """
        Lista todos os usuários cadastrados.
        """
        return self.list_users_use_case.execute()