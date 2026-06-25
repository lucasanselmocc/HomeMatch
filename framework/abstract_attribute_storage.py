"""
framework/abstract_attribute_storage.py
─────────────────────────────────────────
Ponto flexível 3: define como os atributos valorados são persistidos.

O usuário do framework DEVE estender esta classe para indicar ao framework
onde e como salvar os atributos gerados pela análise de IA.

PONTO FIXO: a lógica de agregação por postagem (média dos atributos de fotos)
            e o disparo de atualização de embedding estão no framework
            (SubjectiveAttributeRepository) e não precisam ser reimplementados.
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any, Dict, List


class AbstractAttributeStorage(ABC):
    """
    Contrato para persistência de atributos valorados de uma instância HomeMatch.
    """

    @abstractmethod
    def save_photo_attributes(
        self, photo: Any, attributes: List[Dict[str, Any]]
    ) -> None:
        """
        Persiste os atributos de uma única foto.

        :param photo:       objeto de foto com vínculo à postagem/post
        :param attributes:  lista de {"attribute_token": str, "strength": float}
        """
        raise NotImplementedError

    @abstractmethod
    def refresh_post_aggregates(self, post: Any) -> None:
        """
        Recalcula e persiste os agregados (ex: média) de atributos da postagem
        com base nos atributos individuais de suas fotos.

        Chamado automaticamente pelo framework após save_photo_attributes().
        """
        raise NotImplementedError

    @abstractmethod
    def get_attributes_for_post(self, post: Any) -> List[Dict[str, Any]]:
        """
        Retorna os atributos agregados da postagem.

        Retorno esperado:
            [{"attribute_token": str, "strength_mean": float}, ...]
        """
        raise NotImplementedError
