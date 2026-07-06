"""
examples/dating/strategies/match_score_strategy.py
─────────────────────────────────────────────────
Strategy concreta de match-score para a instância Dating.
"""

from __future__ import annotations

from typing import Any

from framework.abstractions.abstract_match_score_strategy import AbstractMatchScoreStrategy


class DatingMatchScoreStrategy(AbstractMatchScoreStrategy):
    def calculate(self, user: Any, posts: list[Any]) -> list[tuple[Any, int]]:
        scores = []

        for post in posts:
            user_interests = set(getattr(user, "interests", []))
            post_interests = set(getattr(post, "interests", []))

            if not user_interests and not post_interests:
                score = 0
            else:
                common = user_interests.intersection(post_interests)
                total = user_interests.union(post_interests)

                interest_score = len(common) / len(total) * 70 if total else 0
                city_score = (
                    30
                    if getattr(user, "city", None) == getattr(post, "city", None)
                    else 0
                )

                score = round(interest_score + city_score)

            scores.append((post, score))

        return scores

    def persist(self, user: Any, scores: list[tuple[Any, int]]) -> None:
        pass