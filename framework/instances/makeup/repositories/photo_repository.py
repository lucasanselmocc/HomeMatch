
from __future__ import annotations

from typing import Any, Optional

from framework.abstractions.abstract_photo_repository import AbstractPhotoRepository


class MakeupPhotoRepository(AbstractPhotoRepository):
    def __init__(self) -> None:
        self.photos = []

    def create_photo(self, *, post, image, validated_data=None):
        photo = {
            "id": len(self.photos) + 1,
            "post": post,
            "image": image,
            **(validated_data or {}),
        }
        self.photos.append(photo)
        return photo

    def list_photos_by_post(self, post):
        return [photo for photo in self.photos if photo["post"] == post]

    def get_photo_by_id(self, photo_id):
        return next((photo for photo in self.photos if photo["id"] == photo_id), None)

    def delete_photo(self, photo):
        self.photos.remove(photo)