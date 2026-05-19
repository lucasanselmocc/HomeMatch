"""
Testes para o gerenciamento de reviews nos imóveis.

Inclui listagem pública, criação por usuário autenticado, edição e deleção
restritas ao autor.
"""

import pytest
from rest_framework import status


@pytest.mark.django_db
def test_review_list_public(api_client, property_factory):
    prop = property_factory()
    response = api_client.get(f"/api/properties/{prop.id}/reviews/")
    assert response.status_code == status.HTTP_200_OK
    assert "results" in response.data


@pytest.mark.django_db
def test_review_create_authenticated(api_client, property_factory, seeker_user, auth_tokens):
    prop = property_factory()
    tokens = auth_tokens(seeker_user)
    api_client.credentials(HTTP_AUTHORIZATION="Bearer " + tokens["access"])
    data = {"rating": 4, "comment": "Muito bom"}
    response = api_client.post(f"/api/properties/{prop.id}/reviews/", data)
    assert response.status_code == status.HTTP_201_CREATED


@pytest.mark.django_db
def test_review_update_by_author(api_client, property_factory, seeker_user, auth_tokens):
    prop = property_factory()
    tokens = auth_tokens(seeker_user)
    api_client.credentials(HTTP_AUTHORIZATION="Bearer " + tokens["access"])
    # Cria review
    create_resp = api_client.post(f"/api/properties/{prop.id}/reviews/", {"rating": 4, "comment": "Ok"})
    review_id = create_resp.data["id"]
    # Atualiza
    response = api_client.put(
        f"/api/properties/{prop.id}/reviews/{review_id}/",
        {"rating": 5, "comment": "Excelente"},
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.data.get("rating") == 5


@pytest.mark.django_db
def test_review_update_by_other_user_forbidden(
    api_client, property_factory, seeker_user, advertiser_user, auth_tokens
):
    prop = property_factory()
    # Cria review por seeker
    seeker_tokens = auth_tokens(seeker_user)
    api_client.credentials(HTTP_AUTHORIZATION="Bearer " + seeker_tokens["access"])
    create_resp = api_client.post(f"/api/properties/{prop.id}/reviews/", {"rating": 4, "comment": "Bom"})
    review_id = create_resp.data["id"]
    # Tenta editar como advertiser
    adv_tokens = auth_tokens(advertiser_user)
    api_client.credentials(HTTP_AUTHORIZATION="Bearer " + adv_tokens["access"])
    response = api_client.put(
        f"/api/properties/{prop.id}/reviews/{review_id}/",
        {"rating": 3, "comment": "Razoável"},
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_review_delete_by_author(api_client, property_factory, seeker_user, auth_tokens):
    prop = property_factory()
    tokens = auth_tokens(seeker_user)
    api_client.credentials(HTTP_AUTHORIZATION="Bearer " + tokens["access"])
    create_resp = api_client.post(f"/api/properties/{prop.id}/reviews/", {"rating": 4, "comment": "Ok"})
    review_id = create_resp.data["id"]
    response = api_client.delete(f"/api/properties/{prop.id}/reviews/{review_id}/")
    assert response.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.django_db
def test_review_delete_by_other_user_forbidden(
    api_client, property_factory, seeker_user, advertiser_user, auth_tokens
):
    prop = property_factory()
    # Cria review como seeker
    seeker_tokens = auth_tokens(seeker_user)
    api_client.credentials(HTTP_AUTHORIZATION="Bearer " + seeker_tokens["access"])
    create_resp = api_client.post(f"/api/properties/{prop.id}/reviews/", {"rating": 4, "comment": "Ok"})
    review_id = create_resp.data["id"]
    # Tenta deletar como advertiser (não autor)
    adv_tokens = auth_tokens(advertiser_user)
    api_client.credentials(HTTP_AUTHORIZATION="Bearer " + adv_tokens["access"])
    response = api_client.delete(f"/api/properties/{prop.id}/reviews/{review_id}/")
    assert response.status_code == status.HTTP_403_FORBIDDEN