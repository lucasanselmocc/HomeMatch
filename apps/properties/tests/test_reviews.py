"""
Testes para o gerenciamento de reviews nos imóveis.
"""

import pytest
from rest_framework import status
from apps.properties.models import Reviews


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
    
    # Comentário maior que 10 caracteres!
    data = {"rating": 4, "comment": "Achei essa casa fenomenal, muito linda!"}
    response = api_client.post(f"/api/properties/{prop.id}/reviews/", data)
    
    if response.status_code != 201:
        print("ERRO NA CRIAÇÃO DA REVIEW:", response.data)
        
    assert response.status_code == status.HTTP_201_CREATED


@pytest.mark.django_db
def test_review_update_by_author(api_client, property_factory, seeker_user, auth_tokens):
    prop = property_factory()
    tokens = auth_tokens(seeker_user)
    api_client.credentials(HTTP_AUTHORIZATION="Bearer " + tokens["access"])
    
    # Cria a review direto no banco para isolar o teste
    review = Reviews.objects.create(property=prop, user=seeker_user, rating=4, comment="Comentario inicial valido")
    
    # Atualiza via API (usando PATCH para atualização parcial e texto longo)
    response = api_client.patch(
        f"/api/properties/{prop.id}/reviews/{review.id}/",
        {"rating": 5, "comment": "Mudei de ideia, o lugar eh excelente!"},
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.data.get("rating") == 5


@pytest.mark.django_db
def test_review_update_by_other_user_forbidden(api_client, property_factory, seeker_user, advertiser_user, auth_tokens):
    prop = property_factory()
    review = Reviews.objects.create(property=prop, user=seeker_user, rating=4, comment="Comentario inicial valido")
    
    # Tenta editar como advertiser (que não é o dono da review)
    adv_tokens = auth_tokens(advertiser_user)
    api_client.credentials(HTTP_AUTHORIZATION="Bearer " + adv_tokens["access"])
    response = api_client.patch(
        f"/api/properties/{prop.id}/reviews/{review.id}/",
        {"rating": 3, "comment": "Tentando alterar review alheia"},
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_review_delete_by_author(api_client, property_factory, seeker_user, auth_tokens):
    prop = property_factory()
    review = Reviews.objects.create(property=prop, user=seeker_user, rating=4, comment="Comentario inicial valido")
    
    tokens = auth_tokens(seeker_user)
    api_client.credentials(HTTP_AUTHORIZATION="Bearer " + tokens["access"])
    response = api_client.delete(f"/api/properties/{prop.id}/reviews/{review.id}/")
    assert response.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.django_db
def test_review_delete_by_other_user_forbidden(api_client, property_factory, seeker_user, advertiser_user, auth_tokens):
    prop = property_factory()
    review = Reviews.objects.create(property=prop, user=seeker_user, rating=4, comment="Comentario inicial valido")
    
    # Tenta deletar como advertiser (não autor)
    adv_tokens = auth_tokens(advertiser_user)
    api_client.credentials(HTTP_AUTHORIZATION="Bearer " + adv_tokens["access"])
    response = api_client.delete(f"/api/properties/{prop.id}/reviews/{review.id}/")
    assert response.status_code == status.HTTP_403_FORBIDDEN