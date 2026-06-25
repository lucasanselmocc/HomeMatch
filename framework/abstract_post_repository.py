"""
framework/abstract_post_repository.py
───────────────────────────────────────
Ponto flexível 7: define como as postagens (imóveis, perfis, produtos…)
são persistidas.

PONTO FIXO: CRUD de fotos, vinculação com usuário mantenedor e paginação
            são fornecidos pelo framework.
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any, List, Optional


class AbstractPostRepository(ABC):
    """
    Contrato para persistência de postagens de uma instância HomeMatch.
    """

    @abstractmethod
    def create_post(self, *, owner: Any, validated_data: dict) -> Any:
        """
        Cria e persiste uma nova postagem associada a *owner*.

        :param owner:          usuário mantenedor da postagem
        :param validated_data: dados já validados pelo serializer
        """
        raise NotImplementedError

    @abstractmethod
    def save_post(self, post: Any) -> Any:
        """Persiste alterações em uma postagem existente."""
        raise NotImplementedError

    @abstractmethod
    def list_posts(self) -> List[Any]:
        """Retorna todas as postagens ativas, na ordem padrão da instância."""
        raise NotImplementedError

    def get_post_by_id(self, post_id: Any) -> Optional[Any]:
        """
        Busca uma postagem pelo identificador primário.
        Implementação padrão retorna None; sobrescreva conforme o modelo.
        """
        return None
