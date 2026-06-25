"""
framework/use_cases/upload_post_photo_use_case.py
────────────────────────────────────────────────
Use case fixo do framework responsável por associar uma foto a uma postagem.

Fluxo fixo:
  1. Recebe uma postagem
  2. Recebe uma imagem/arquivo
  3. Valida os dados mínimos
  4. Usa o repositório da instância para salvar a foto
  5. Retorna a foto criada

Ponto flexível usado:
  - AbstractPhotoRepository
"""

from __future__ import annotations

from typing import Any

from framework.abstract_photo_repository import AbstractPhotoRepository


class UploadPostPhotoUseCase:
    """
    Caso de uso fixo para upload/associação de fotos a uma postagem.

    O framework controla o fluxo geral.
    A instância define como a foto será salva.
    """

    def __init__(self, photo_repository: AbstractPhotoRepository) -> None:
        self.photo_repository = photo_repository

    def execute(
        self,
        *,
        post: Any,
        image: Any,
        validated_data: dict | None = None,
    ) -> Any:
        """
        Cria uma foto associada a uma postagem.

        :param post: postagem à qual a foto será associada
        :param image: arquivo/imagem enviada
        :param validated_data: dados adicionais já validados, se existirem
        :return: foto criada
        """
        self._validate_input(post=post, image=image, validated_data=validated_data)

        return self.photo_repository.create_photo(
            post=post,
            image=image,
            validated_data=validated_data or {},
        )

    def _validate_input(
        self,
        *,
        post: Any,
        image: Any,
        validated_data: dict | None,
    ) -> None:
        """
        Valida os dados mínimos necessários para criar uma foto.
        """
        if post is None:
            raise ValueError("A postagem é obrigatória.")

        if image is None:
            raise ValueError("A imagem é obrigatória.")

        if validated_data is not None and not isinstance(validated_data, dict):
            raise TypeError("Os dados adicionais da foto devem estar em formato de dicionário.")