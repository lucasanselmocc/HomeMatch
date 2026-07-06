"""
apps/ai_analysis/attribute_storage.py
────────────────────────────────────
Implementação concreta do armazenamento de atributos subjetivos do HomeMatch.
"""

from __future__ import annotations

from typing import Any

from framework.abstractions.abstract_attribute_storage import AbstractAttributeStorage

from apps.ai_analysis.models import (
    PhotoSubjectiveAttribute,
    PropertySubjectiveAttribute,
)
from apps.ai_analysis.repositories import SubjectiveAttributeRepository


class HomeMatchAttributeStorage(AbstractAttributeStorage):
    """
    Storage concreto de atributos subjetivos do HomeMatch.

    No domínio imobiliário, os atributos subjetivos são gerados por IA
    a partir das fotos dos imóveis.
    """

    def save_photo_attributes(self, photo: Any, attributes: list[dict]) -> None:
        """
        Persiste os atributos subjetivos de uma foto.
        """
        SubjectiveAttributeRepository.replace_photo_attributes(
            photo=photo,
            attributes=attributes,
        )

    def refresh_post_aggregates(self, post: Any) -> None:
        """
        Atualiza os atributos médios da postagem/imóvel.
        """
        SubjectiveAttributeRepository.refresh_property_aggregates(post)

    def get_attributes_for_post(self, post: Any) -> list[dict]:
        """
        Retorna os atributos subjetivos médios de um imóvel.
        """
        return list(
            PropertySubjectiveAttribute.objects.filter(property=post).values(
                "attribute_token",
                "strength_mean",
            )
        )

    def get_photo_attributes(self, *, photo: Any) -> list[dict]:
        """
        Retorna os atributos subjetivos de uma foto.
        """
        return list(
            PhotoSubjectiveAttribute.objects.filter(photo=photo).values(
                "attribute_token",
                "strength",
            )
        )