"""
framework/ai/gemini_ai_analyzer.py
─────────────────────────────────
Analyzer padrão do framework que usa Gemini para análise de imagens.
"""

from __future__ import annotations

from typing import Any

from framework.abstractions.abstract_ai_analyzer import AbstractAIAnalyzer
from framework.abstractions.abstract_ai_analysis_config import (
    AbstractAIAnalysisConfig,
)
from framework.ai.exceptions import AIAnalysisError
from framework.ai.gemini_client import GeminiClient
from framework.ai.gemini_parser import GeminiParser


class GeminiAIAnalyzer(AbstractAIAnalyzer):
    """
    Implementação padrão baseada em Gemini.

    O framework faz a chamada da API.
    A instância fornece prompt e schema.
    """

    def __init__(
        self,
        *,
        config: AbstractAIAnalysisConfig,
        client: GeminiClient | None = None,
        parser: GeminiParser | None = None,
    ) -> None:
        self.config = config
        self.client = client or GeminiClient()
        self.parser = parser or GeminiParser()

    def analyze_photo(
        self,
        photo: Any,
        prompt: str | None = None,
    ) -> list[dict]:
        """
        Analisa uma foto e retorna atributos valorados.
        """
        final_prompt = prompt or self.config.get_prompt()
        schema = self.config.get_schema()
        image = self._extract_image(photo)

        try:
            response = self.client.analyze_photo(
                image=image,
                prompt=final_prompt,
                schema=schema,
            )

            return self.parser.extract_attributes(response)

        except Exception as exc:
            raise AIAnalysisError(f"Erro ao analisar foto com Gemini: {exc}") from exc

    def _extract_image(self, photo: Any) -> Any:
        """
        Extrai a imagem a partir do objeto de foto da instância.
        """
        for attribute in ("image", "file", "image_file", "image_url", "r2_key"):
            if hasattr(photo, attribute):
                return getattr(photo, attribute)

        return photo