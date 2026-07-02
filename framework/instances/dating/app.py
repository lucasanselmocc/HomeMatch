"""
instances/dating/app.py
─────────────────────
Instância concreta do framework para uma aplicação de encontros.
"""

from __future__ import annotations

from framework.framework import HomeMatchFramework

from framework.instances.dating.attribute_storage import DatingAttributeStorage

from framework.instances.dating.repositories.user_repository import DatingUserRepository
from framework.instances.dating.repositories.post_repository import DatingPostRepository
from framework.instances.dating.repositories.photo_repository import DatingPhotoRepository

from framework.instances.dating.strategies.ai_analyzer import DatingAIAnalyzer
from framework.instances.dating.strategies.match_score import DatingMatchScoreStrategy
from framework.instances.dating.strategies.search_pool import DatingSearchPool


def create_dating_app() -> HomeMatchFramework:
    """
    Cria a instância Dating utilizando o framework.
    """
    return HomeMatchFramework(
        user_repository=DatingUserRepository(),
        post_repository=DatingPostRepository(),
        photo_repository=DatingPhotoRepository(),
        attribute_storage=DatingAttributeStorage(),
        ai_analyzer=DatingAIAnalyzer(),
        match_score_strategy=DatingMatchScoreStrategy(),
        search_pool=DatingSearchPool(),
    )