"""
framework/instances/makeup/strategies/match_score_strategy.py
────────────────────────────────────────────────────────────
Strategy concreta de match-score para a instância Makeup.
"""

from __future__ import annotations

from typing import Any

from framework.abstractions.abstract_match_score_strategy import (
    AbstractMatchScoreStrategy,
)


class MakeupMatchScoreStrategy(AbstractMatchScoreStrategy):
    """
    Calcula a compatibilidade entre um usuário e produtos de maquiagem.
    """

    def calculate(
        self,
        user: Any,
        posts: list[Any],
    ) -> list[tuple[Any, int]]:
        """
        Calcula um score de compatibilidade para cada produto.
        """
        scores: list[tuple[Any, int]] = []

        for post in posts:
            score = 0

            # Compatibilidade do tipo de pele
            if (
                getattr(user, "skin_type", None)
                == getattr(post, "skin_type", None)
            ):
                score += 40

            # Compatibilidade do acabamento desejado
            if (
                getattr(user, "preferred_finish", None)
                == getattr(post, "finish", None)
            ):
                score += 35

            # Compatibilidade do orçamento
            if (
                getattr(post, "price", 0)
                <= getattr(user, "max_price", float("inf"))
            ):
                score += 25

            scores.append((post, score))

        return scores

    def persist(
        self,
        user: Any,
        scores: list[tuple[Any, int]],
    ) -> None:
        """
        Persiste os scores calculados.

        Nesta instância de demonstração não existe persistência.
        """
        pass