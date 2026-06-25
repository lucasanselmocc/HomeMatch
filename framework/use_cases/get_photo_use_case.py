"""
framework/use_cases/get_photo_by_id_use_case.py
───────────────────────────────────────────────
Use case fixo do framework responsável por buscar uma foto pelo ID.

Fluxo fixo:
  1. Recebe o ID da foto
  2. Valida se o ID foi informado
  3. Solicita ao repositório da instância a busca da foto
  4. Retorna a foto encontrada

Ponto flexível usado:
  - AbstractPhotoRepository
"""

from __future__ import annotations

from typing import Any

from framework.abstract_photo_repository import AbstractPhotoRepository


class GetPhotoByIdUseCase:
    """
    Caso de uso fixo para buscar uma foto pelo identificador.

    O framework define o fluxo de busca.
    A instância define como a foto será recuperada do banco.
    """

    def __init__(self, photo_repository: AbstractPhotoRepository) -> None:
        self.photo_repository = photo_repository

    def execute(self, *, photo_id: Any) -> Any:
        """
        Busca uma foto pelo ID.

        :param photo_id: identificador da foto
        :return: foto encontrada
        """
        self._validate_input(photo_id=photo_id)

        photo = self.photo_repository.get_photo_by_id(photo_id)

        if photo is None:
            raise ValueError("Foto não encontrada.")

        return photo

    def _validate_input(self, *, photo_id: Any) -> None:
        """
        Valida os dados mínimos necessários para buscar uma foto.
        """
        if photo_id is None:
            raise ValueError("O ID da foto é obrigatório.")