from __future__ import annotations

from typing import Any

from framework.abstractions.abstract_post_repository import AbstractPostRepository
from framework.instances.demo_models import DemoObject


class DatingPostRepository(AbstractPostRepository):
    def __init__(self) -> None:
        self.posts: list[Any] = []

    def create_post(self, *, owner: Any, validated_data: dict) -> Any:
        post = DemoObject(
            id=len(self.posts) + 1,
            owner=owner,
            **validated_data,
        )

        self.posts.append(post)
        return post

    def save_post(self, post: Any) -> Any:
        """
        Em memória não há persistência real.
        """
        return post

    def list_posts(self) -> list[Any]:
        return self.posts

    def get_post_by_id(self, post_id: Any) -> Any:
        return next(
            (post for post in self.posts if post.id == post_id),
            None,
        )

    def delete_post(self, post: Any) -> None:
        self.posts.remove(post)

    def filter_posts(self, criteria: dict) -> list[Any]:
        """
        Para a demonstração, retorna todas as postagens.
        """
        return self.posts