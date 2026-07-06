"""
framework/instances/demo.py
──────────────────────────
Demonstração de reutilização do framework nas instâncias Dating e Makeup.
"""

from framework.instances.dating.app import create_dating_app
from framework.instances.makeup.app import create_makeup_app

from framework.instances.dating.strategies.ai_analyzer import DatingAIAnalyzer
from framework.instances.makeup.strategies.ai_analyzer import MakeupAIAnalyzer


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


if __name__ == "__main__":
    #run_dating_demo()
    run_makeup_demo()