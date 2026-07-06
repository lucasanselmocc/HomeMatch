"""
framework/instances/dating/strategies/ai_analyzer.py
────────────────────────────────────────────────────
Strategy concreta de análise por IA para a instância Dating.
"""

from __future__ import annotations

from typing import Any

from framework.abstractions.abstract_ai_analyzer import AbstractAIAnalyzer


class DatingAIAnalyzer(AbstractAIAnalyzer):
    """Analisador demonstrativo para perfis de encontros."""

    def analyze_photo(self, photo: Any, prompt: str | None = None) -> list[dict]:
        return [
            {"attribute_token": "lifestyle.outdoor", "strength": 0.8},
            {"attribute_token": "personality.casual", "strength": 0.7},
            {"attribute_token": "social.smile", "strength": 0.9},
        ]
