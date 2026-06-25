"""
framework/use_cases/delete_post_photo_use_case.py
────────────────────────────────────────────────
Use case fixo do framework responsável pela remoção de uma foto associada
a uma postagem.

Fluxo fixo:
  1. Recebe uma foto existente
  2. Valida se a foto foi informada
  3. Solicita ao repositório da instância a remoção da foto

Ponto flexível usado:
  - AbstractPhotoRepository
"""

from __future__ import annotations

from typing import Any

from framework.abstract_photo_repository import AbstractPhotoRepository


class DeletePostPhotoUseCase:
    """
    Caso de uso fixo para exclusão de fotos de uma postagem.

    O framework controla o fluxo geral de remoção.
    A instância define como a foto será removida do banco ou do sistema de arquivos.
    """

    def __init__(self, photo_repository: AbstractPhotoRepository) -> None:
        self.photo_repository = photo_repository

    def execute(self, *, photo: Any) -> None:
        """
        Remove uma foto existente.

        :param photo: foto que será removida
        """
        self._validate_input(photo=photo)

        self.photo_repository.delete_photo(photo)

    def _validate_input(self, *, photo: Any) -> None:
        """
        Valida os dados mínimos necessários para remover uma foto.
        """
        if photo is None:
            raise ValueError("A foto é obrigatória.")