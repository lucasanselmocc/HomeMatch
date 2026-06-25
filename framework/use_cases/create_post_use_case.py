"""
framework/use_cases/create_post_use_case.py
──────────────────────────────────────────
Use case fixo do framework responsável pela criação de postagens.

Fluxo fixo:
  1. Recebe o usuário mantenedor da postagem
  2. Recebe os dados já validados da postagem
  3. Valida os dados mínimos
  4. Cria a postagem usando o repositório da instância
  5. Retorna a postagem criada

Ponto flexível usado:
  - AbstractPostRepository
"""

from __future__ import annotations

from typing import Any

from framework.abstract_post_repository import AbstractPostRepository


class CreatePostUseCase:
    """
    Caso de uso fixo para criação de postagens.

    O framework controla o fluxo geral de criação.
    A instância define como a postagem será persistida.
    """

    def __init__(self, post_repository: AbstractPostRepository) -> None:
        self.post_repository = post_repository

    def execute(self, *, owner: Any, validated_data: dict) -> Any:
        """
        Cria uma nova postagem associada a um usuário mantenedor.

        :param owner: usuário dono/mantenedor da postagem
        :param validated_data: dados da postagem já validados pela camada de entrada
        :return: postagem criada
        """
        self._validate_input(
            owner=owner,
            validated_data=validated_data,
        )

        return self.post_repository.create_post(
            owner=owner,
            validated_data=validated_data,
        )

    def _validate_input(self, *, owner: Any, validated_data: dict) -> None:
        """
        Valida os dados mínimos necessários para criar uma postagem.
        """
        if owner is None:
            raise ValueError("O usuário mantenedor da postagem é obrigatório.")

        if validated_data is None:
            raise ValueError("Os dados da postagem são obrigatórios.")

        if not isinstance(validated_data, dict):
            raise TypeError("Os dados da postagem devem estar em formato de dicionário.")