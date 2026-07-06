from __future__ import annotations

from typing import Any

from framework.abstractions.abstract_post_repository import AbstractPostRepository
from framework.instances.demo_models import DemoObject


class MakeupPostRepository(AbstractPostRepository):
    """
    Repositório em memória de postagens da instância Makeup.
    """

    def __init__(self) -> None:
        self.posts: list[Any] = []

    def create_post(self, *, owner: Any, validated_data: dict) -> Any:
        """
        Cria um novo produto de maquiagem.
        """
        post = DemoObject(
            id=len(self.posts) + 1,
            owner=owner,
            **validated_data,
        )

        self.posts.append(post)
        return post

    def save_post(self, post: Any) -> Any:
        """
        Persiste alterações na postagem.

        Como esta é uma implementação em memória, basta retornar
        o próprio objeto.
        """
        return post

    def list_posts(self) -> list[Any]:
        """
        Retorna todas as postagens cadastradas.
        """
        return self.posts

    def get_post_by_id(self, post_id: Any) -> Any:
        """
        Busca uma postagem pelo identificador.
        """
        return next(
            (post for post in self.posts if post.id == post_id),
            None,
        )

    def delete_post(self, post: Any) -> None:
        """
        Remove uma postagem.
        """
        self.posts.remove(post)

    def filter_posts(self, criteria: dict) -> list[Any]:
        """
        Filtra postagens.

        Nesta implementação de demonstração, todos os produtos
        cadastrados são retornados.
        """
        return self.posts