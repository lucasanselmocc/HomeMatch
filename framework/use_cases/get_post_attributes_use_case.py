"""
framework/use_cases/get_post_attributes_use_case.py
──────────────────────────────────────────────────
Use case fixo do framework responsável por recuperar os atributos agregados
de uma postagem.

Fluxo fixo:
  1. Recebe uma postagem
  2. Valida se a postagem foi informada
  3. Solicita ao storage os atributos agregados da postagem
  4. Retorna a lista de atributos

Ponto flexível usado:
  - AbstractAttributeStorage
"""

from __future__ import annotations

from typing import Any, Dict, List

from framework.abstract_attribute_storage import AbstractAttributeStorage


class GetPostAttributesUseCase:
    """
    Caso de uso fixo para recuperar atributos agregados de uma postagem.

    O framework define que uma postagem pode possuir atributos valorados.
    A instância define como esses atributos são persistidos e recuperados.
    """

    def __init__(self, attribute_storage: AbstractAttributeStorage) -> None:
        self.attribute_storage = attribute_storage

    def execute(self, *, post: Any) -> List[Dict[str, Any]]:
        """
        Retorna os atributos agregados de uma postagem.

        :param post: postagem cujos atributos serão recuperados
        :return: lista de atributos agregados
        """
        self._validate_input(post=post)

        return self.attribute_storage.get_attributes_for_post(post)

    def _validate_input(self, *, post: Any) -> None:
        """
        Valida os dados mínimos necessários para buscar atributos da postagem.
        """
        if post is None:
            raise ValueError("A postagem é obrigatória.")