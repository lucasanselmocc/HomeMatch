"""
framework/abstract_match_score_strategy.py
────────────────────────────────────────────
Ponto flexível 4: define a lógica de cálculo do match-score entre usuários.

O usuário do framework DEVE estender esta classe para:
  - implementar a lógica de cálculo do score (calculate)
  - persistir o resultado (persist)

PONTO FIXO: a entidade MatchScore e a lógica de comparação entre usuários
            (MatchScoreUseCase) são fornecidas pelo framework.
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any, List, Tuple


class AbstractMatchScoreStrategy(ABC):
    """
    Contrato para a estratégia de cálculo de match-score de uma instância.
    """

    @abstractmethod
    def calculate(
        self, user: Any, posts: List[Any]
    ) -> List[Tuple[Any, int]]:
        """
        Calcula um score de compatibilidade entre *user* e cada postagem.

        :param user:   objeto de usuário autenticado
        :param posts:  lista de postagens/perfis candidatos
        :return:       lista de (post, score_0_a_100)
        """
        raise NotImplementedError

    @abstractmethod
    def persist(self, user: Any, scores: List[Tuple[Any, int]]) -> None:
        """
        Persiste os scores calculados (ex: salvar em MatchScore no banco).

        :param user:    objeto de usuário
        :param scores:  lista de (post, score) retornada por calculate()
        """
        raise NotImplementedError

    # ── helper concreto (ponto fixo) ─────────────────────────────────────────
    def calculate_and_persist(self, user: Any, posts: List[Any]) -> List[Tuple[Any, int]]:
        """
        Orquestra calculate() + persist() em uma única chamada.
        Pode ser sobrescrito se a instância precisar de atomicidade.
        """
        scores = self.calculate(user, posts)
        self.persist(user, scores)
        return scores
