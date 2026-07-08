"""
config/homematch_framework.py
─────────────────────────────
Integração da aplicação Django HomeMatch com o framework reutilizável.
"""

from __future__ import annotations

from framework.instances.real_estate.app import create_real_estate_app


def get_homematch_framework() -> HomeMatchFramework:
    """
    Cria a instância concreta do framework para o domínio imobiliário.
    """
    return HomeMatchFramework(
        user_repository=UserRepository(),
        post_repository=DjangoPostRepository(),
        photo_repository=PhotoRepository(),
        attribute_storage=HomeMatchAttributeStorage(),
        ai_analyzer=HomeMatchAIAnalyzer(),
        match_score_strategy=HomeMatchMatchScoreStrategy(),
        search_pool=HomeMatchSearchPool(),
    )