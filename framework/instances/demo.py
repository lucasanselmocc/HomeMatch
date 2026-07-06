"""
framework/instances/demo.py
──────────────────────────
Demonstração de reutilização do framework nas instâncias Dating e Makeup.
"""

import os

from framework.instances.dating.app import create_dating_app
from framework.instances.makeup.app import create_makeup_app

from framework.instances.dating.strategies.ai_analyzer import DatingAIAnalyzer
from framework.instances.makeup.strategies.ai_analyzer import MakeupAIAnalyzer


def bootstrap_django_settings() -> bool:
    if os.environ.get("DJANGO_SETTINGS_MODULE") is None:
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

    try:
        import django

        django.setup()
        return True
    except ImportError:
        print("Django is not installed. Skipping Real Estate demo.")
        return False
    except Exception as exc:
        print(f"Unable to bootstrap Django settings: {exc}. Skipping Real Estate demo.")
        return False


def run_dating_demo():
    print("\n=== Dating App ===")

    app = create_dating_app(
        ai_analyzer=DatingAIAnalyzer(),
        query_interpreter=None,
    )

    user = app.users.create_user(
        email="ana@email.com",
        name="Ana",
        user_type="cliente",
        password="123",
    )

    user.interests = ["praia", "viagem", "filmes"]
    user.city = "Campo Grande"

    profile = app.posts.create_post(
        owner=user,
        validated_data={
            "bio": "Gosto de praia, esportes e viagens.",
            "interests": ["praia", "esportes", "viagem"],
            "hobbies": ["corrida", "cinema"],
            "city": "Campo Grande",
            "lifestyle": "outdoor",
        },
    )

    photo = app.photos.upload_photo(
        post=profile,
        image="dating_photo.jpg",
        validated_data={"order": 1},
    )

    attributes = app.analyzer.analyze_photo(
        photo=photo,
        prompt="Analise o perfil da foto.",
    )

    results = app.search.search_posts(
        query="pessoa que gosta de praia e viagem",
    )

    scores = app.match_score.calculate_match_score(
        user=user,
        posts=[profile],
    )

    print("Usuário:", user)
    print("Perfil criado:", profile)
    print("Foto criada:", photo)
    print("Atributos gerados:", attributes)
    print("Resultado da busca:", results)
    print("Match-score:", scores)


def run_makeup_demo():
    print("\n=== Makeup App ===")

    app = create_makeup_app(
        ai_analyzer=MakeupAIAnalyzer(),
        query_interpreter=None,
    )

    user = app.users.create_user(
        email="bia@email.com",
        name="Bia",
        user_type="cliente",
        password="123",
    )

    user.skin_type = "oleosa"
    user.preferred_finish = "natural"
    user.max_price = 80

    product = app.posts.create_post(
        owner=user,
        validated_data={
            "name": "Base Natural Glow",
            "brand": "BeautyLab",
            "category": "base",
            "description": "Base leve para pele oleosa com acabamento natural.",
            "skin_type": "oleosa",
            "finish": "natural",
            "color": "bege médio",
            "price": 65,
        },
    )

    photo = app.photos.upload_photo(
        post=product,
        image="makeup_photo.jpg",
        validated_data={"order": 1},
    )

    attributes = app.analyzer.analyze_photo(
        photo=photo,
        prompt="Analise a imagem do produto.",
    )

    results = app.search.search_posts(
        query="base para pele oleosa acabamento natural",
    )

    scores = app.match_score.calculate_match_score(
        user=user,
        posts=[product],
    )

    print("Usuário:", user)
    print("Produto criado:", product)
    print("Foto criada:", photo)
    print("Atributos gerados:", attributes)
    print("Resultado da busca:", results)
    print("Match-score:", scores)


def run_real_estate_demo():
    print("\n=== Real Estate App ===")
    from framework.instances.real_estate.app import create_real_estate_app
    app = create_real_estate_app()

    user = app.users.get_user_by_email(email="carlos@email.com")
    if user is None:
        user = app.users.create_user(
            email="carlos@email.com",
            name="Carlos",
            user_type="S",
            password="123",
        )

    user.city = "São Paulo"
    user.preferred_price_range = (250000, 650000)
    user.preferred_property_type = "A"

    property_item = app.posts.create_post(
        owner=user,
        validated_data={
            "property_purpose": "S",
            "type": "A",
            "area": 85.0,
            "floors": 1,
            "floor_number": 7,
            "price": 420000.00,
            "address": "Av. Paulista, 1000",
            "neighborhood": "Bela Vista",
            "city": "São Paulo",
            "has_mobilia": False,
            "status": True,
            "latitude": -23.561414,
            "longitude": -46.655881,
            "description": "Apartamento moderno com boa iluminação e vista panorâmica.",
            "rooms": {"bedrooms": 2, "bathrooms": 2, "parking_spots": 1},
            "rooms_extras": {
                "living_room": True,
                "garden": False,
                "kitchen": True,
                "laundry_room": True,
                "pool": False,
                "office": False,
            },
            "condo": {
                "name": "Palmeiras Garden",
                "address": "Rua Augusta, 1250",
                "gym": True,
                "pool": True,
                "court": False,
                "parks": True,
                "party_spaces": False,
                "concierge": True,
            },
        },
    )

    photo = app.photos.upload_photo(
        post=property_item,
        image="real_estate_photo.jpg",
        validated_data={"order": 1},
    )

    attributes = app.analyzer.analyze_photo(
        photo=photo,
        prompt="Analise a imagem do imóvel.",
    )

    results = app.search.search_posts(
        query="Apartamento com boa iluminação e vista panorâmica",
    )

    scores = app.match_score.calculate_match_score(
        user=user,
        posts=[property_item],
    )

    print("Usuário:", user)
    print("Imóvel criado:", property_item)
    print("Foto criada:", photo)
    print("Atributos gerados:", attributes)
    print("Resultado da busca:", results)
    print("Match-score:", scores)


if __name__ == "__main__":
    run_dating_demo()
    run_makeup_demo()

    if bootstrap_django_settings():
        run_real_estate_demo()
