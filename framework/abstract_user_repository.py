"""
framework/abstract_user_repository.py
───────────────────────────────────────
Ponto flexível 6: define como os usuários são persistidos.

PONTO FIXO: as rotas de autenticação JWT, CRUD de usuário e validações
            básicas (e-mail único) são fornecidas pelo framework.
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any, Optional


class AbstractUserRepository(ABC):
    """
    Contrato para persistência de usuários de uma instância HomeMatch.
    """

    @abstractmethod
    def create_user(self, *, email: str, name: str, user_type: str, password: str) -> Any:
        """Cria e persiste um novo usuário."""
        raise NotImplementedError

    @abstractmethod
    def email_exists(self, email: str) -> bool:
        """Verifica se já existe um usuário com o e-mail informado."""
        raise NotImplementedError

    @abstractmethod
    def save_user(self, user: Any) -> Any:
        """Persiste alterações em um usuário existente."""
        raise NotImplementedError

    def get_by_email(self, email: str) -> Optional[Any]:
        """
        Busca usuário por e-mail.
        Implementação padrão retorna None; sobrescreva se necessário.
        """
        return None
