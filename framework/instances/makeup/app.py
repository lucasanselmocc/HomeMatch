"""
instances/makeup/app.py
─────────────────────
Instância concreta do framework para uma aplicação de maquiagens.
"""

from __future__ import annotations

from framework.framework import HomeMatchFramework

from framework.instances.makeup.attribute_storage import MakeupAttributeStorage

from framework.instances.makeup.repositories.user_repository import MakeupUserRepository
from framework.instances.makeup.repositories.post_repository import MakeupPostRepository
from framework.instances.makeup.repositories.photo_repository import MakeupPhotoRepository

from framework.instances.makeup.strategies.ai_analyzer import MakeupAIAnalyzer
from framework.instances.makeup.strategies.match_score import MakeupMatchScoreStrategy
from framework.instances.makeup.strategies.search_pool import MakeupSearchPool


def create_makeup_app() -> HomeMatchFramework:
    """
    Cria a instância Makeup utilizando o framework.
    """
    return HomeMatchFramework(
        user_repository=MakeupUserRepository(),
        post_repository=MakeupPostRepository(),
        photo_repository=MakeupPhotoRepository(),
        attribute_storage=MakeupAttributeStorage(),
        ai_analyzer=MakeupAIAnalyzer(),
        match_score_strategy=MakeupMatchScoreStrategy(),
        search_pool=MakeupSearchPool(),
    )
