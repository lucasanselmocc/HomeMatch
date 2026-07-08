"""
framework/services/match_score_service.py
────────────────────────────────────────
Service fixo do framework responsável pelo cálculo do match-score.
"""

from __future__ import annotations

from typing import Any

from framework.use_cases.calc_match_score_use_case import CalculateMatchScoreUseCase


class MatchScoreService:
    """Service responsável pelo cálculo e ranking de compatibilidade."""

    def __init__(
        self,
        calc_match_score_use_case: CalculateMatchScoreUseCase,
    ) -> None:
        self.calc_match_score_use_case = calc_match_score_use_case

    def calculate_match_score(self, **kwargs):
        """Calcula o match-score usando o caso de uso fixo do framework."""
        return self.calc_match_score_use_case.execute(**kwargs)

    def rank_matches(
        self,
        *,
        targets: list[Any] | None = None,
        posts: list[Any] | None = None,
        user: Any,
        query_params: dict | None = None,
    ) -> list[Any]:
        """
        Calcula o match-score de uma coleção e retorna os itens ordenados.

        Mantém compatibilidade com a view imobiliária, que chama
        rank_matches(targets=...), e com o contrato base do framework,
        que usa posts.
        """
        candidate_posts = list(targets if targets is not None else posts or [])

        strategy = self.calc_match_score_use_case.match_score_strategy

        if hasattr(strategy, "rank"):
            return strategy.rank(
                targets=candidate_posts,
                user=user,
                query_params=query_params,
            )

        scores = self.calculate_match_score(user=user, posts=candidate_posts)

        for post, score in scores:
            setattr(post, "match_score", score)

        return [
            post
            for post, _ in sorted(
                scores,
                key=lambda item: item[1],
                reverse=True,
            )
        ]
