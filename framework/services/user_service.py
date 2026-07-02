"""
framework/services/user_service.py
─────────────────────────────────
Service fixo do framework responsável por agrupar os casos de uso
relacionados ao gerenciamento de usuários.

Esta classe fornece uma interface simplificada para que aplicações
concretas utilizem as funcionalidades do framework sem precisar
interagir diretamente com cada caso de uso.
"""

from __future__ import annotations

from framework.use_cases.create_user_use_case import CreateUserUseCase
from framework.use_cases.get_user_use_case import GetUserByEmailUseCase
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
    ) -> None:
        """
        Inicializa o service com os casos de uso necessários.
        """
        self.create_user_use_case = create_user_use_case
        self.get_user_use_case = get_user_use_case
        self.update_user_use_case = update_user_use_case

    def create_user(
        self,
        *,
        email: str,
        name: str,
        user_type: str,
        password: str,
    ):
        """
        Cria um novo usuário.

        A operação é delegada ao caso de uso responsável pela criação.
        """
        return self.create_user_use_case.execute(
            email=email,
            name=name,
            user_type=user_type,
            password=password,
        )

    def get_user(self, user_id):
        """
        Recupera um usuário pelo identificador.
        """
        return self.get_user_use_case.execute(user_id=user_id)

    def update_user(self, **kwargs):
        """
        Atualiza os dados de um usuário.

        A validação e a persistência são delegadas ao caso de uso
        correspondente.
        """
        return self.update_user_use_case.execute(**kwargs)