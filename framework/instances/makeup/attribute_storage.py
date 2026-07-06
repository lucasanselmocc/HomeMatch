"""
examples/makeup/attribute_storage.py
───────────────────────────────────
Storage concreto de atributos para a instância Makeup.
"""

from __future__ import annotations

from typing import Any

from framework.abstractions.abstract_attribute_storage import AbstractAttributeStorage


class MakeupAttributeStorage(AbstractAttributeStorage):
    def __init__(self) -> None:
        self.photo_attributes: dict[int, list[dict]] = {}
        self.post_attributes: dict[int, list[dict]] = {}

    def save_photo_attributes(self, photo: Any, attributes: list[dict]) -> None:
        self.photo_attributes[photo.id] = attributes
        self.refresh_post_aggregates(photo.post)

    def refresh_post_aggregates(self, post: Any) -> None:
        related_attributes = []

        for attributes in self.photo_attributes.values():
            related_attributes.extend(attributes)

        self.post_attributes[post.id] = related_attributes

    def get_attributes_for_post(self, post: Any) -> list[dict]:
        return self.post_attributes.get(post.id, [])