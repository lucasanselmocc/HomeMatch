from __future__ import annotations

from typing import Any, Optional

from django.shortcuts import get_object_or_404

from framework.abstractions.abstract_user_repository import AbstractUserRepository

from apps.properties.models import Properties
from apps.users.models import SearchPreference, User


class UserRepository(AbstractUserRepository):
    """
    Repositório concreto de usuários do HomeMatch usando o ORM do Django.
    """

    def create_user(
        self,
        *,
        email: str,
        name: str,
        user_type: str,
        password: str,
    ) -> Any:
        return User.objects.create_user(
            email=email,
            name=name,
            user_type=user_type,
            password=password,
        )

    def email_exists(self, email: str) -> bool:
        return User.objects.filter(email=email).exists()

    def save_user(self, user: Any) -> Any:
        user.save()
        return user

    def get_by_email(self, email: str) -> Optional[Any]:
        return User.objects.filter(email=email).first()

    def delete_user(self, user: Any) -> None:
        user.delete()

    def list_users(self) -> list[Any]:
        return list(User.objects.all())


class SearchPreferenceRepository:
    @staticmethod
    def upsert_for_user(user, preferences_data):
        SearchPreference.objects.update_or_create(
            user=user,
            defaults=preferences_data,
        )


class FavoriteRepository:
    @staticmethod
    def list_favorites(user):
        return user.favorites.all()

    @staticmethod
    def get_property_or_404(property_id):
        return get_object_or_404(Properties, id=property_id)

    @staticmethod
    def add_favorite(user, property_obj):
        user.favorites.add(property_obj)

    @staticmethod
    def remove_favorite(user, property_obj):
        user.favorites.remove(property_obj)