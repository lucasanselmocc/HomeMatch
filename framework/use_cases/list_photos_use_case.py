"""
framework/use_cases/list_post_photos_use_case.py
───────────────────────────────────────────────
Use case fixo do framework responsável por listar as fotos associadas
a uma postagem.

Fluxo fixo:
  1. Recebe uma postagem
  2. Valida se a postagem foi informada
  3. Solicita ao repositório da instância as fotos da postagem
  4. Retorna a lista de fotos

Ponto flexível usado:
  - AbstractPhotoRepository
"""

from __future__ import annotations

from typing import Any, List

from framework.abstract_photo_repository import AbstractPhotoRepository


class ListPostPhotosUseCase:
    """
    Caso de uso fixo para listagem de fotos de uma postagem.

    O framework define que uma postagem pode possuir fotos.
    A instância define como essas fotos são buscadas no banco.
    """

    def __init__(self, photo_repository: AbstractPhotoRepository) -> None:
        self.photo_repository = photo_repository

    def execute(self, *, post: Any) -> List[Any]:
        """
        Lista todas as fotos associadas a uma postagem.

        :param post: postagem cujas fotos serão listadas
        :return: lista de fotos
        """
        self._validate_input(post=post)

        return self.photo_repository.list_photos_by_post(post)

    def _validate_input(self, *, post: Any) -> None:
        """
        Valida os dados mínimos necessários para listar fotos.
        """
        if post is None:
            raise ValueError("A postagem é obrigatória.")