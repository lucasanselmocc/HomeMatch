"""
examples/makeup/strategies/ai_analyzer.py
────────────────────────────────────────
Strategy concreta de análise por IA para a instância Makeup.
"""

from __future__ import annotations

from typing import Any

from framework.abstractions.abstract_ai_analyzer import AbstractAIAnalyzer


class MakeupAIAnalyzer(AbstractAIAnalyzer):
    """
    Analisador fictício para imagens de produtos de maquiagem.
    """

    def analyze_photo(self, *, photo: Any, prompt: str) -> list[dict]:
        return [
            {"attribute_token": "finish.glow", "strength": 0.8},
            {"attribute_token": "texture.creamy", "strength": 0.7},
            {"attribute_token": "color.warm", "strength": 0.6},
        ]