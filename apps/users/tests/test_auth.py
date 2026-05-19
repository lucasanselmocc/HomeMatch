"""
Testes de autenticação para o aplicativo de usuários.

Cobre registro, login, refresh e logout, incluindo casos de erro como
credenciais inválidas ou emails duplicados.
"""

import pytest
from rest_framework import status


@pytest.mark.django_db
def test_register_user_success(api_client):
    data = {
        "name": "Novo Usuário",
        "email": "novo@example.com",
        "password": "password123",
        "user_type": "S",
    }
    response = api_client.post("/api/users/register/", data)
    assert response.status_code == status.HTTP_201_CREATED


@pytest.mark.django_db
def test_register_duplicate_email(api_client, create_user):
    # Cria usuário com email duplicado
    create_user(name="Usuário Existente", email="dup@example.com", user_type="S", password="password123")
    data = {
        "name": "Outro Usuário",
        "email": "dup@example.com",
        "password": "password123",
        "user_type": "S",
    }
    response = api_client.post("/api/users/register/", data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_login_success(api_client, create_user):
    user = create_user(name="Usuário Teste", email="login@example.com", user_type="S", password="password123")
    response = api_client.post(
        "/api/users/login/",
        {"email": user.email, "password": "password123"},
    )
    assert response.status_code == status.HTTP_200_OK
    assert "access" in response.data and "refresh" in response.data


@pytest.mark.django_db
def test_login_invalid_credentials(api_client, create_user):
    user = create_user(name="Usuário Teste", email="invalid@example.com", user_type="S", password="password123")
    response = api_client.post(
        "/api/users/login/",
        {"email": user.email, "password": "senhaerrada"},
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_token_refresh(api_client, create_user):
    user = create_user(name="Usuário Refresh", email="refresh@example.com", user_type="S", password="password123")
    login_resp = api_client.post(
        "/api/users/login/",
        {"email": user.email, "password": "password123"},
    )
    refresh_token = login_resp.data["refresh"]
    response = api_client.post("/api/users/token/refresh/", {"refresh": refresh_token})
    assert response.status_code == status.HTTP_200_OK
    assert "access" in response.data


@pytest.mark.django_db
def test_logout_blacklists_refresh(api_client, create_user):
    user = create_user(name="Usuário Logout", email="logout@example.com", user_type="S", password="password123")
    login_resp = api_client.post(
        "/api/users/login/",
        {"email": user.email, "password": "password123"},
    )
    refresh_token = login_resp.data["refresh"]
    # Efetua logout
    response = api_client.post("/api/users/logout/", {"refresh": refresh_token})
    # TokenBlacklistView pode retornar 200 ou 205 depending on version
    assert response.status_code in [status.HTTP_205_RESET_CONTENT, status.HTTP_200_OK]
    # Tenta usar o mesmo refresh token novamente
    refresh_resp = api_client.post("/api/users/token/refresh/", {"refresh": refresh_token})
    assert refresh_resp.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_400_BAD_REQUEST]