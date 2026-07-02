"""
examples/dating/attribute_storage.py
───────────────────────────────────
Storage concreto de atributos para a instância Dating.
"""

from __future__ import annotations

from typing import Any

from framework.abstractions.abstract_attribute_storage import AbstractAttributeStorage


class DatingAttributeStorage(AbstractAttributeStorage):
    def __init__(self) -> None:
        self.photo_attributes = {}
        self.post_attributes = {}

    def save_photo_attributes(self, photo, attributes):
        self.photo_attributes[photo["id"]] = attributes
        self.refresh_post_aggregates(photo["post"])

    def refresh_post_aggregates(self, post):
        post_id = post["id"]

        related_attributes = []
        for attributes in self.photo_attributes.values():
            related_attributes.extend(attributes)

        self.post_attributes[post_id] = related_attributes

    def get_attributes_for_post(self, post):
        return self.post_attributes.get(post["id"], [])