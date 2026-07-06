"""
framework/abstract_photo_repository.py
──────────────────────────────────────
Ponto flexível: define como as fotos associadas às postagens são persistidas.

PONTO FIXO: o fluxo de upload, associação com postagem e remoção de fotos
é controlado pelos use cases do framework.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, List, Optional


class AbstractPhotoRepository(ABC):
    """
    Contrato para persistência de fotos de uma instância HomeMatch.
    """

    @abstractmethod
    def create_photo(self, *, post: Any, image: Any, validated_data: dict | None = None) -> Any:
        """
        Cria e persiste uma foto associada a uma postagem.
        """
        raise NotImplementedError

    @abstractmethod
    def list_photos_by_post(self, post: Any) -> List[Any]:
        """
        Lista as fotos associadas a uma postagem.
        """
        raise NotImplementedError
    
    @abstractmethod
    def get_photo_by_id(self, photo_id: Any) -> Optional[Any]:
        """
        Busca uma foto pelo identificador.
        """
        raise NotImplementedError

    @abstractmethod
    def delete_photo(self, photo: Any) -> None:
        """
        Remove uma foto existente.
        """
        raise NotImplementedError
