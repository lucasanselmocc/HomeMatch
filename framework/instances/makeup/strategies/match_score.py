"""
examples/makeup/strategies/match_score_strategy.py
────────────────────────────────────────────────
Strategy concreta de match-score para a instância Makeup.
"""

from __future__ import annotations

from typing import Any

from framework.abstractions.abstract_match_score_strategy import AbstractMatchScoreStrategy


class MakeupMatchScoreStrategy(AbstractMatchScoreStrategy):
    """
    Calcula compatibilidade entre usuário e produto de maquiagem.
    """

    def calculate(self, *, user: Any, target: Any, **kwargs) -> int:
        score = 0

        if user.get("skin_type") == target.get("skin_type"):
            score += 40

        if user.get("preferred_finish") == target.get("finish"):
            score += 35

        if target.get("price", 0) <= user.get("max_price", float("inf")):
            score += 25

        return score
    
    def persist(self, user, target, score):
        """
        Persiste/loga o match-score calculado.

        Nesta instância de demonstração, não há persistência real.
        """
        pass