"""
Testes para operações relacionadas a imóveis.

Inclui listagem pública, filtros, criação, atualização e exclusão, com
verificações de permissões conforme o tipo de usuário (advertiser ou seeker).
"""

import pytest
from rest_framework import status

from apps.properties.models import Rooms


@pytest.mark.django_db
def test_property_list_public(api_client, property_factory):
    # Cria ao menos uma propriedade
    property_factory()
    response = api_client.get("/api/properties/")
    assert response.status_code == status.HTTP_200_OK
    # A listagem usa paginação, então a chave results deve existir
    assert "results" in response.data


@pytest.mark.django_db
def test_property_filters(api_client, property_factory):
    # Uma propriedade barata e outra cara
    property_factory(price=500)
    property_factory(price=1500)
    response = api_client.get("/api/properties/?min_price=1000")
    assert response.status_code == status.HTTP_200_OK
    # Esperamos apenas a propriedade acima de 1000
    assert len(response.data["results"]) == 1
@pytest.mark.django_db
def test_property_create_by_advertiser(api_client, advertiser_user, auth_tokens):
    tokens = auth_tokens(advertiser_user)
    api_client.credentials(HTTP_AUTHORIZATION="Bearer " + tokens["access"])
    
    data = {
        "property_purpose": "S",
        "type": "H",
        "area": 120,
        "floors": 2,
        "floor_number": 0,
        "price": 2500,
        "address": "Rua das Casas",
        "neighborhood": "Centro",
        "city": "Natal",
        "has_mobilia": False,
        "status": True,
        "description": "Casa ampla",
        "embedding": "[]",
        "rooms": {
            "bedrooms": 2,
            "bathrooms": 2,
            "parking_spots": 1
        },
        "rooms_extras": {}
    }
    response = api_client.post("/api/properties/", data, format="json")
    assert response.status_code == status.HTTP_201_CREATED


@pytest.mark.django_db
def test_property_create_by_seeker_forbidden(api_client, seeker_user, auth_tokens):
    tokens = auth_tokens(seeker_user)
    api_client.credentials(HTTP_AUTHORIZATION="Bearer " + tokens["access"])
    
    data = {
        "property_purpose": "R",
        "type": "A",
        "area": 60,
        "floors": 1,
        "floor_number": 1,
        "price": 800,
        "address": "Rua das Avenidas",
        "neighborhood": "Centro",
        "city": "Natal",
        "has_mobilia": False,
        "status": True,
        "description": "Apartamento",
        "embedding": "[]",
        "rooms": {
            "bedrooms": 1,
            "bathrooms": 1,
            "parking_spots": 1
        },
        "rooms_extras": {}
    }
    response = api_client.post("/api/properties/", data, format="json")
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_property_update_by_owner(api_client, advertiser_user, property_factory, auth_tokens):
    # Cria uma propriedade pertencente ao advertiser
    prop = property_factory()
    tokens = auth_tokens(advertiser_user)
    api_client.credentials(HTTP_AUTHORIZATION="Bearer " + tokens["access"])
    # Atualiza preço via PATCH
    response = api_client.patch(f"/api/properties/{prop.id}/", {"price": 1100})
    assert response.status_code == status.HTTP_200_OK
    assert response.data.get("price") == "1100.00"


@pytest.mark.django_db
def test_property_update_by_other_user_forbidden(api_client, seeker_user, property_factory, auth_tokens):
    prop = property_factory()
    tokens = auth_tokens(seeker_user)
    api_client.credentials(HTTP_AUTHORIZATION="Bearer " + tokens["access"])
    response = api_client.patch(f"/api/properties/{prop.id}/", {"price": 1300})
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_property_delete_by_owner(api_client, advertiser_user, property_factory, auth_tokens):
    prop = property_factory()
    tokens = auth_tokens(advertiser_user)
    api_client.credentials(HTTP_AUTHORIZATION="Bearer " + tokens["access"])
    response = api_client.delete(f"/api/properties/{prop.id}/")
    assert response.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.django_db
def test_property_delete_by_other_user_forbidden(api_client, seeker_user, property_factory, auth_tokens):
    prop = property_factory()
    tokens = auth_tokens(seeker_user)
    api_client.credentials(HTTP_AUTHORIZATION="Bearer " + tokens["access"])
    response = api_client.delete(f"/api/properties/{prop.id}/")
    assert response.status_code == status.HTTP_403_FORBIDDEN