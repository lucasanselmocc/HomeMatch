"""
examples/dating/strategies/match_score_strategy.py
─────────────────────────────────────────────────
Strategy concreta de match-score para a instância Dating.
"""

from __future__ import annotations

from typing import Any

from framework.abstractions.abstract_match_score_strategy import AbstractMatchScoreStrategy


class DatingMatchScoreStrategy(AbstractMatchScoreStrategy):
    """
    Calcula compatibilidade entre usuários/perfis de encontros.
    """

    def calculate(self, *, user: Any, target: Any, **kwargs) -> int:
        user_interests = set(user.get("interests", []))
        target_interests = set(target.get("interests", []))

        if not user_interests and not target_interests:
            return 0

        common = user_interests.intersection(target_interests)
        total = user_interests.union(target_interests)

        interest_score = len(common) / len(total) * 70 if total else 0
        city_score = 30 if user.get("city") == target.get("city") else 0

        return round(interest_score + city_score)
    
    def persist(self, user, target, score):
        """
        Persiste/loga o match-score calculado.

        Nesta instância de demonstração, não há persistência real.
        """
        pass