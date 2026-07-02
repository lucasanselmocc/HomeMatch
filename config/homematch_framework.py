"""
config/homematch_framework.py
─────────────────────────────
Integração da aplicação Django HomeMatch com o framework reutilizável.
"""

from __future__ import annotations

from framework.framework import HomeMatchFramework

from apps.users.repositories import UserRepository
from apps.properties.repositories import DjangoPostRepository
from apps.properties.repositories import PhotoRepository
from apps.ai_analysis.attribute_storage import HomeMatchAttributeStorage

from apps.ai_analysis.strategies import HomeMatchAIAnalyzer
from apps.properties.strategies import HomeMatchMatchScoreStrategy
from apps.search.strategies import HomeMatchSearchPool


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