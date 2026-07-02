"""
framework/services/post_service.py
─────────────────────────────────
Service fixo do framework responsável por agrupar os casos de uso
relacionados ao gerenciamento de postagens.

Esta classe fornece uma interface simplificada para que aplicações
concretas manipulem postagens sem acessar diretamente os casos de uso.
"""

from __future__ import annotations

from framework.use_cases.create_post_use_case import CreatePostUseCase
from framework.use_cases.delete_post_use_case import DeletePostUseCase
from framework.use_cases.get_post_use_case import GetPostByIdUseCase
from framework.use_cases.get_post_attributes_use_case import GetPostAttributesUseCase
from framework.use_cases.list_post_use_case import ListPostsUseCase
from framework.use_cases.update_post_use_case import UpdatePostUseCase


class PostService:
    """
    Service responsável pelo gerenciamento de postagens.

    Esta classe agrupa os casos de uso relacionados às postagens,
    disponibilizando uma interface única para as aplicações.
    """

    def __init__(
        self,
        create_post_use_case: CreatePostUseCase,
        update_post_use_case: UpdatePostUseCase,
        delete_post_use_case: DeletePostUseCase,
        get_post_use_case: GetPostByIdUseCase,
        list_post_use_case: ListPostsUseCase,
        get_post_attributes_use_case: GetPostAttributesUseCase,
    ) -> None:
        """
        Inicializa o service com os casos de uso necessários.
        """
        self.create_post_use_case = create_post_use_case
        self.update_post_use_case = update_post_use_case
        self.delete_post_use_case = delete_post_use_case
        self.get_post_use_case = get_post_use_case
        self.list_post_use_case = list_post_use_case
        self.get_post_attributes_use_case = get_post_attributes_use_case

    def create_post(self, **kwargs):
        """Cria uma nova postagem."""
        return self.create_post_use_case.execute(**kwargs)

    def update_post(self, **kwargs):
        """Atualiza uma postagem existente."""
        return self.update_post_use_case.execute(**kwargs)

    def delete_post(self, **kwargs):
        """Remove uma postagem."""
        return self.delete_post_use_case.execute(**kwargs)

    def get_post(self, **kwargs):
        """Recupera uma postagem."""
        return self.get_post_use_case.execute(**kwargs)

    def list_posts(self, **kwargs):
        """Lista as postagens cadastradas."""
        return self.list_post_use_case.execute(**kwargs)

    def get_post_attributes(self, **kwargs):
        """Obtém os atributos associados a uma postagem."""
        return self.get_post_attributes_use_case.execute(**kwargs)