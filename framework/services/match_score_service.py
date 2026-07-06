"""
framework/services/match_score_service.py
────────────────────────────────────────
Service fixo do framework responsável pelo cálculo do match-score.

O algoritmo de cálculo é definido por uma estratégia concreta
fornecida pela aplicação que utiliza o framework.
"""

from __future__ import annotations

from framework.use_cases.calc_match_score_use_case import CalculateMatchScoreUseCase


class MatchScoreService:
    """
    Service responsável pelo cálculo de compatibilidade.

    Esta classe encapsula o caso de uso responsável pelo cálculo
    do match-score entre entidades do domínio.
    """

    def __init__(
        self,
        calc_match_score_use_case: CalculateMatchScoreUseCase,
    ) -> None:
        """
        Inicializa o service com o caso de uso necessário.
        """
        self.calc_match_score_use_case = calc_match_score_use_case

    def calculate_match_score(self, **kwargs):
        """
        Calcula o match-score entre duas entidades.
        """
        return self.calc_match_score_use_case.execute(**kwargs)