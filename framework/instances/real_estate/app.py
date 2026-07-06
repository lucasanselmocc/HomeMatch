"""
instances/real_estate/app.py
────────────────────────────
Instância concreta do framework para a aplicação imobiliária.
"""

from __future__ import annotations

from framework.framework import HomeMatchFramework

from framework.instances.real_estate.attribute_storage import RealEstateAttributeStorage
from framework.instances.real_estate.repositories import (
    RealEstateUserRepository,
    RealEstatePostRepository,
    RealEstatePhotoRepository,
)
from framework.instances.real_estate.ai_analyzer import RealEstateAIAnalyzer
from framework.instances.real_estate.match_score_strategy import RealEstateMatchScoreStrategy
from framework.instances.real_estate.search_pool import RealEstateSearchPool


def create_real_estate_app() -> HomeMatchFramework:
    """
    Cria a instância RealEstate utilizando o framework.
    """
    return HomeMatchFramework(
        user_repository=RealEstateUserRepository(),
        post_repository=RealEstatePostRepository(),
        photo_repository=RealEstatePhotoRepository(),
        attribute_storage=RealEstateAttributeStorage(),
        ai_analyzer=RealEstateAIAnalyzer(),
        match_score_strategy=RealEstateMatchScoreStrategy(),
        search_pool=RealEstateSearchPool(),
    )
