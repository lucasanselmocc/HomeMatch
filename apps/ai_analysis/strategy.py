"""
apps/ai_analysis/strategies.py
──────────────────────────────
Strategies concretas de análise por IA do HomeMatch.
"""

from __future__ import annotations

from typing import Any

from django.conf import settings

from framework.abstractions.abstract_ai_analyzer import AbstractAIAnalyzer

from apps.ai_analysis.client import AiVisionClient
from apps.ai_analysis.exceptions import AiAnalysisError
from apps.ai_analysis.parser import AiAttributeParser


class HomeMatchAIAnalyzer(AbstractAIAnalyzer):
    """
    Strategy concreta responsável por analisar fotos de imóveis
    e gerar atributos subjetivos.
    """

    def __init__(
        self,
        base_url: str | None = None,
        api_key: str | None = None,
        model: str | None = None,
        client: AiVisionClient | None = None,
    ) -> None:
        base_url = base_url or settings.AI_API_BASE_URL
        api_key = api_key or settings.AI_API_KEY
        model = model or settings.AI_MODEL

        if not base_url or not api_key:
            raise ValueError(
                "AI_API_BASE_URL and AI_API_KEY must be set in settings / environment."
            )

        self.client = client or AiVisionClient(
            base_url=base_url,
            api_key=api_key,
            model=model,
        )

    def analyze_photo(self, photo: Any, prompt: str | None = None) -> list[dict]:
        """
        Analisa uma foto e retorna os atributos extraídos pela IA.
        """
        if not prompt:
            return []

        try:
            response = self.client.analyze_photo(photo, prompt)
            return AiAttributeParser.extract_attributes(response)
        except Exception as exc:
            raise AiAnalysisError(f"Photo {photo.pk}: {exc}") from exc