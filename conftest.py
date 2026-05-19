"""
Fixtures reutilizáveis para a suíte de testes do HomeMatch.
"""

import pytest
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken

from apps.properties.models import Properties, Rooms, RoomsExtras


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def create_user(db):
    def make_user(**kwargs):
        User = get_user_model()
        password = kwargs.pop("password", "password123")
        user = User.objects.create(**kwargs)
        user.set_password(password)
        user.save()
        return user
    return make_user


@pytest.fixture
def advertiser_user(create_user):
    return create_user(name="Advertiser User", email="advertiser@example.com", user_type="A", password="password123")


@pytest.fixture
def seeker_user(create_user):
    return create_user(name="Seeker User", email="seeker@example.com", user_type="S", password="password123")


@pytest.fixture
def property_factory(db, advertiser_user):
    def make_property(**kwargs):
        # Usa get_or_create para evitar erro de quarto repetido (UniqueConstraint)
        rooms, _ = Rooms.objects.get_or_create(
            bedrooms=kwargs.pop("bedrooms", 1),
            bathrooms=kwargs.pop("bathrooms", 1),
            parking_spots=kwargs.pop("parking_spots", 1)
        )
        extras, _ = RoomsExtras.objects.get_or_create()

        defaults = {
            "owner": advertiser_user,
            "rooms": rooms,
            "rooms_extras": extras,
            "property_purpose": "R",
            "type": "A",
            "area": 50,
            "floors": 1,
            "floor_number": 1,
            "price": 1000,
            "address": "Rua Teste",
            "neighborhood": "Centro",
            "city": "Natal",
            "has_mobilia": False,
            "status": True,
            "description": "Propriedade de teste",
        }
        defaults.update(kwargs)
        return Properties.objects.create(**defaults)

    return make_property


@pytest.fixture
def auth_tokens():
    def _tokens(user):
        refresh = RefreshToken.for_user(user)
        return {"access": str(refresh.access_token), "refresh": str(refresh)}
    return _tokens