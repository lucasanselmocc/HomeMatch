from __future__ import annotations

from typing import Any, Optional

from framework.abstractions.abstract_user_repository import AbstractUserRepository
from framework.instances.demo_models import DemoObject


class MakeupUserRepository(AbstractUserRepository):
    def __init__(self) -> None:
        self.users: list[Any] = []

    def create_user(self, *, email, name, user_type, password):
        user = DemoObject(
        id=len(self.users) + 1,
        email=email,
        name=name,
        user_type=user_type,
        password=password,
        )
        self.users.append(user)
        return user

    def email_exists(self, email: str) -> bool:
        return any(user["email"] == email for user in self.users)

    def save_user(self, user: Any) -> Any:
        return user

    def get_by_email(self, email: str) -> Optional[Any]:
        return next((user for user in self.users if user["email"] == email), None)

    def delete_user(self, user: Any) -> None:
        self.users.remove(user)

    def list_users(self) -> list[Any]:
        return self.users