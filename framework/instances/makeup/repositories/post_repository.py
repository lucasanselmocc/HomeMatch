from __future__ import annotations

from typing import Any, Optional

from framework.abstractions.abstract_post_repository import AbstractPostRepository

class MakeupPostRepository(AbstractPostRepository):
    def __init__(self) -> None:
        self.posts: list[Any] = []

    def create_post(self, **kwargs):
        post = {"id": len(self.posts) + 1, **kwargs}
        self.posts.append(post)
        return post

    def update_post(self, *, post, validated_data):
        post.update(validated_data)
        return post

    def delete_post(self, post):
        self.posts.remove(post)

    def get_by_id(self, post_id: int):
        return next((post for post in self.posts if post["id"] == post_id), None)

    def list_posts(self):
        return self.posts

    def filter_posts(self, criteria: dict):
        return self.posts
    
    def save_post(self, post):
        return post
