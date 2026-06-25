"""
framework/use_cases/update_post_use_case.py
──────────────────────────────────────────
Use case fixo do framework responsável pela atualização de postagens.

Fluxo fixo:
  1. Recebe uma postagem existente
  2. Recebe os dados atualizados
  3. Valida os dados mínimos
  4. Aplica as alterações na postagem
  5. Salva usando o repositório da instância
  6. Retorna a postagem atualizada

Ponto flexível usado:
  - AbstractPostRepository
"""

from __future__ import annotations

from typing import Any

from framework.abstract_post_repository import AbstractPostRepository


class UpdatePostUseCase:
    """
    Caso de uso fixo para atualização de postagens.

    O framework controla o fluxo geral de atualização.
    A instância define como a postagem é persistida.
    """

    def __init__(self, post_repository: AbstractPostRepository) -> None:
        self.post_repository = post_repository

    def execute(self, *, post: Any, validated_data: dict) -> Any:
        """
        Atualiza uma postagem existente.

        :param post: postagem que será atualizada
        :param validated_data: dados já validados pela camada de entrada
        :return: postagem atualizada
        """
        self._validate_input(
            post=post,
            validated_data=validated_data,
        )

        for field, value in validated_data.items():
            setattr(post, field, value)

        return self.post_repository.save_post(post)

    def _validate_input(self, *, post: Any, validated_data: dict) -> None:
        """
        Valida os dados mínimos necessários para atualizar uma postagem.
        """
        if post is None:
            raise ValueError("A postagem é obrigatória.")

        if validated_data is None:
            raise ValueError("Os dados da postagem são obrigatórios.")

        if not isinstance(validated_data, dict):
            raise TypeError("Os dados da postagem devem estar em formato de dicionário.")