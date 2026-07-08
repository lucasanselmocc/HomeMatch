"""
framework/instances/makeup/strategies/ai_analyzer.py
────────────────────────────────────────────────────
Strategy concreta de análise por IA para a instância Makeup.

Delega para GeminiAIAnalyzer, em framework/ai/ 
configurado com o prompt/schema específico da instância
(DatingPhotoAnalysisConfig). Nenhuma lógica de chamada à API é duplicada
aqui, já que o ponto fixo do framework cuida disso.

"""

from __future__ import annotations

import logging
from typing import Any

from framework.abstractions.abstract_ai_analyzer import AbstractAIAnalyzer
from framework.ai.exceptions import AIAnalysisError
from framework.ai.gemini_ai_analyzer import GeminiAIAnalyzer
from framework.instances.makeup.photo_analysis_config import (
    MakeupPhotoAnalysisConfig,
)

logger = logging.getLogger(__name__)

# Usado apenas quando a IA real não pôde ser chamada (ex.: foto de demo sem
# conteúdo de imagem real, ou API indisponível).
_DEMO_FALLBACK_ATTRIBUTES: list[dict] = [
    {"attribute_token": "finish.glow", "strength": 0.8},
    {"attribute_token": "texture.creamy", "strength": 0.7},
    {"attribute_token": "color.warm", "strength": 0.6},
]


class MakeupAIAnalyzer(AbstractAIAnalyzer):
    """Analisador real de fotos de produtos de maquiagem, via Gemini."""

    def __init__(self, gemini_analyzer: GeminiAIAnalyzer | None = None) -> None:
        # Injeção de dependência: facilita testes (basta passar um analyzer
        # falso). A construção do GeminiClient real é adiada (lazy) para
        # dentro de analyze_photo — assim, ambientes sem GEMINI_API_KEY
        # configurada (ex.: `framework/instances/demo.py`) continuam
        # funcionando offline via fallback, em vez de quebrar já no
        # __init__.
        self._gemini_analyzer = gemini_analyzer

    def _get_gemini_analyzer(self) -> GeminiAIAnalyzer:
        if self._gemini_analyzer is None:
            self._gemini_analyzer = GeminiAIAnalyzer(config=MakeupPhotoAnalysisConfig())
        return self._gemini_analyzer

    def analyze_photo(self, photo: Any, prompt: str | None = None) -> list[dict]:
        try:
            return self._get_gemini_analyzer().analyze_photo(photo, prompt)
        except (AIAnalysisError, ValueError) as exc:
            # AIAnalysisError -> a chamada ao Gemini falhou (ex.: foto de
            #   demo sem conteúdo de imagem real).
            # ValueError       -> não foi possível nem construir o cliente
            #   (ex.: GEMINI_API_KEY ausente no ambiente).
            logger.warning(
                "Falha na análise de IA (Makeup) para a foto %s; "
                "usando atributos de demonstração como fallback: %s",
                getattr(photo, "id", "?"),
                exc,
            )
            return _DEMO_FALLBACK_ATTRIBUTES
