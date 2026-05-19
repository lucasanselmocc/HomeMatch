"""
Testes para a funcionalidade de favoritos de imóveis.

Inclui operações de listar, adicionar e remover favoritos, garantindo que
usuários não autenticados recebam o status apropriado.
"""

import pytest
from rest_framework import status


@pytest.mark.django_db
def test_get_favorites_authenticated(api_client, seeker_user, property_factory, auth_tokens):
    # Cria duas propriedades
    prop1 = property_factory()
    prop2 = property_factory()
    # Adiciona uma propriedade aos favoritos do usuário
    seeker_user.favorites.add(prop1)
    tokens = auth_tokens(seeker_user)
    api_client.credentials(HTTP_AUTHORIZATION="Bearer " + tokens["access"])
    response = api_client.get("/api/users/favorites/")
    assert response.status_code == status.HTTP_200_OK
    # Deve retornar apenas os favoritos do usuário (1 item)
    assert isinstance(response.data, list)
    assert len(response.data) == 1


@pytest.mark.django_db
def test_add_favorite(api_client, seeker_user, property_factory, auth_tokens):
    prop = property_factory()
    tokens = auth_tokens(seeker_user)
    api_client.credentials(HTTP_AUTHORIZATION="Bearer " + tokens["access"])
    response = api_client.post("/api/users/favorites/", {"property_id": prop.id})
    assert response.status_code == status.HTTP_200_OK
    # Verifica se a propriedade está nos favoritos
    assert seeker_user.favorites.filter(id=prop.id).exists()


@pytest.mark.django_db
def test_remove_favorite(api_client, seeker_user, property_factory, auth_tokens):
    prop = property_factory()
    seeker_user.favorites.add(prop)
    tokens = auth_tokens(seeker_user)
    api_client.credentials(HTTP_AUTHORIZATION="Bearer " + tokens["access"])
    # A API espera property_id no corpo da requisição
    response = api_client.delete("/api/users/favorites/", {"property_id": prop.id})
    assert response.status_code == status.HTTP_200_OK
    assert not seeker_user.favorites.filter(id=prop.id).exists()


@pytest.mark.django_db
def test_favorites_unauthenticated(api_client):
    response = api_client.get("/api/users/favorites/")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED