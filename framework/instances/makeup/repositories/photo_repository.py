from __future__ import annotations

from typing import Any, Optional

from framework.abstractions.abstract_photo_repository import AbstractPhotoRepository
from framework.instances.demo_models import DemoObject


class MakeupPhotoRepository(AbstractPhotoRepository):
    """Repositório em memória para fotos dos produtos de maquiagem."""

    def __init__(self) -> None:
        self.photos: list[Any] = []

    def create_photo(
        self,
        *,
        post: Any,
        image: Any,
        validated_data: dict | None = None,
    ) -> Any:
        photo = DemoObject(
            id=len(self.photos) + 1,
            post=post,
            image=image,
            **(validated_data or {}),
        )
        self.photos.append(photo)
        return photo

    def list_photos_by_post(self, post: Any) -> list[Any]:
        return [photo for photo in self.photos if getattr(photo, "post", None) == post]

    def get_photo_by_id(self, photo_id: Any) -> Optional[Any]:
        return next(
            (photo for photo in self.photos if getattr(photo, "id", None) == photo_id),
            None,
        )

    def delete_photo(self, photo: Any) -> None:
        self.photos.remove(photo)
