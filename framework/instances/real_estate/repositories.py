"""
framework/instances/real_estate/repositories.py
─────────────────────────────────────────────────
Instância 1 (Plataforma Imobiliária) — pontos flexíveis 6 e 7.

RealEstateUserRepository → estende AbstractUserRepository
RealEstatePostRepository → estende AbstractPostRepository

Ambas delegam para os repositórios Django existentes (apps/users e
apps/properties), demonstrando que a instância imobiliária reutiliza
a camada de dados original sem reimplementação.
"""

from __future__ import annotations
import io
from typing import Any, List, Optional

from apps.properties.models import Properties
from apps.properties.repositories import PhotoRepository as DjangoPropertyPhotoRepository
from apps.properties.repositories import PropertyRepository
from apps.users.repositories import UserRepository as _DjangoUserRepo
from framework.abstractions.abstract_post_repository import AbstractPostRepository
from framework.abstractions.abstract_photo_repository import AbstractPhotoRepository


class _DemoImageFile(io.BytesIO):
    def __init__(self, name: str, content: bytes | None = None):
        super().__init__(content or b"demo image content")
        self.name = name
        self.content_type = "image/jpeg"

    def chunks(self):
        self.seek(0)
        yield self.read()
from framework.abstractions.abstract_user_repository import AbstractUserRepository


# ─────────────────────────────────────────────────────────────────────────────
# Ponto flexível 6 — Repositório de usuários
# ─────────────────────────────────────────────────────────────────────────────

class RealEstateUserRepository(AbstractUserRepository):
    """
    Repositório de usuários para a Plataforma Imobiliária.
    Delega para apps.users.repositories.UserRepository (ponto fixo).
    """

    def __init__(self) -> None:
        self._repository = _DjangoUserRepo()

    def create_user(
        self, *, email: str, name: str, user_type: str, password: str
    ) -> Any:
        return self._repository.create_user(
            email=email, name=name, user_type=user_type, password=password
        )

    def email_exists(self, email: str) -> bool:
        return self._repository.email_exists(email)

    def save_user(self, user: Any) -> Any:
        return self._repository.save_user(user)

    def get_by_email(self, email: str) -> Optional[Any]:
        from apps.users.models import User
        return User.objects.filter(email=email).first()

    def delete_user(self, user: Any) -> None:
        return self._repository.delete_user(user)

    def list_users(self) -> list[Any]:
        return self._repository.list_users()


# ─────────────────────────────────────────────────────────────────────────────
# Ponto flexível 7 — Repositório de postagens (imóveis)
# ─────────────────────────────────────────────────────────────────────────────

class RealEstatePostRepository(AbstractPostRepository):
    """
    Repositório de postagens para a Plataforma Imobiliária.
    A "postagem" aqui é um objeto Properties (imóvel).
    """

    def create_post(self, *, owner: Any, validated_data: dict) -> Any:
        """
        Cria um imóvel usando o repositório de propriedades do Django.
        """
        return PropertyRepository().create_post(owner=owner, validated_data=validated_data)

    def save_post(self, post: Any) -> Any:
        return PropertyRepository().save_post(post)

    def list_posts(self) -> List[Any]:
        return PropertyRepository().list_posts()

    def get_post_by_id(self, post_id: Any) -> Optional[Any]:
        return PropertyRepository().get_by_id(post_id)

    def delete_post(self, post: Any) -> None:
        PropertyRepository().delete_post(post)

    def filter_posts(self, criteria: dict) -> list[Any]:
        return list(Properties.objects.filter(**criteria).order_by("created_at"))


class RealEstatePhotoRepository(AbstractPhotoRepository):
    """
    Repositório de fotos para a Plataforma Imobiliária.
    Delegação para o repositório de fotos do aplicativo de propriedades.
    """

    def __init__(self) -> None:
        self._repository = DjangoPropertyPhotoRepository()

    def create_photo(
        self,
        *,
        post: Any,
        image: Any,
        validated_data: dict | None = None,
    ) -> Any:
        validated_data = validated_data or {}
        order = validated_data.get("order", 1)
        if isinstance(image, str):
            image = _DemoImageFile(name=image)
        return self._repository.create_photo(post=post, image=image, order=order)

    def list_photos_by_post(self, post: Any) -> List[Any]:
        return self._repository.list_by_post(post)

    def get_photo_by_id(self, photo_id: Any) -> Optional[Any]:
        return self._repository.get_by_id(photo_id)

    def delete_photo(self, photo: Any) -> None:
        self._repository.delete_photo(photo)
