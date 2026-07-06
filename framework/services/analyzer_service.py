"""
framework/services/analyzer_service.py
─────────────────────────────────────
Service fixo do framework responsável por agrupar os casos de uso
relacionados à análise de imagens e postagens.

As estratégias concretas de análise são fornecidas pelas aplicações
que utilizam o framework.
"""

from __future__ import annotations

from framework.use_cases.analyze_photo_use_case import AnalyzePhotoUseCase
from framework.use_cases.analyze_post_use_case import AnalyzePostUseCase


class AnalyzerService:
    """
    Service responsável pela análise automática de fotos e postagens.

    Esta classe centraliza as operações relacionadas à geração
    de atributos por meio de analisadores concretos.
    """

    def __init__(
        self,
        analyze_photo_use_case: AnalyzePhotoUseCase,
        analyze_post_use_case: AnalyzePostUseCase,
    ) -> None:
        """
        Inicializa o service com os casos de uso necessários.
        """
        self.analyze_photo_use_case = analyze_photo_use_case
        self.analyze_post_use_case = analyze_post_use_case

    def analyze_photo(self, **kwargs):
        """
        Analisa uma foto e gera seus atributos.
        """
        return self.analyze_photo_use_case.execute(**kwargs)

    def analyze_post(self, **kwargs):
        """
        Analisa uma postagem a partir das fotos associadas.
        """
        return self.analyze_post_use_case.execute(**kwargs)