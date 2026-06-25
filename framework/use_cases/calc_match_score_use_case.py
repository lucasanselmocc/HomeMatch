"""
framework/use_cases/calculate_match_score_use_case.py
────────────────────────────────────────────────────
Use case fixo do framework responsável por calcular o match-score entre
um usuário e uma lista de postagens candidatas.

Fluxo fixo:
  1. Recebe um usuário
  2. Recebe uma lista de postagens candidatas
  3. Valida os dados de entrada
  4. Usa uma estratégia concreta para calcular os scores
  5. Persiste os scores calculados
  6. Retorna os resultados

Ponto flexível usado:
  - AbstractMatchScoreStrategy
"""

from __future__ import annotations

from typing import Any, List, Tuple

from framework.abstract_match_score_strategy import AbstractMatchScoreStrategy


class CalculateMatchScoreUseCase:
    """
    Caso de uso fixo para cálculo de match-score.

    O framework controla o fluxo geral.
    A instância define a regra concreta de compatibilidade.
    """

    def __init__(self, match_score_strategy: AbstractMatchScoreStrategy) -> None:
        self.match_score_strategy = match_score_strategy

    def execute(self, *, user: Any, posts: List[Any]) -> List[Tuple[Any, int]]:
        """
        Calcula e persiste o match-score entre um usuário e várias postagens.

        :param user: usuário para quem o match será calculado
        :param posts: lista de postagens candidatas
        :return: lista de tuplas (post, score)
        """
        self._validate_input(user=user, posts=posts)

        scores = self.match_score_strategy.calculate_and_persist(
            user=user,
            posts=posts,
        )

        self._validate_scores(scores)

        return scores

    def _validate_input(self, *, user: Any, posts: List[Any]) -> None:
        """
        Valida os dados mínimos necessários para calcular o match-score.
        """
        if user is None:
            raise ValueError("O usuário é obrigatório.")

        if posts is None:
            raise ValueError("A lista de postagens é obrigatória.")

        if not isinstance(posts, list):
            raise TypeError("As postagens devem estar em formato de lista.")

    def _validate_scores(self, scores: List[Tuple[Any, int]]) -> None:
        """
        Valida se os scores retornados pela estratégia estão no formato esperado.
        """
        if scores is None:
            raise ValueError("A estratégia de match-score retornou None.")

        for post, score in scores:
            if post is None:
                raise ValueError("A estratégia retornou uma postagem inválida.")

            if not isinstance(score, int):
                raise TypeError("O score deve ser um número inteiro.")

            if score < 0 or score > 100:
                raise ValueError("O score deve estar entre 0 e 100.")