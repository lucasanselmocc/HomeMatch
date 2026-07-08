"""
framework/instances/dating/photo_analysis_config.py
─────────────────────────────────────────────────────
Instância Dating: configuração de análise visual por IA.

Implementa AbstractAIAnalysisConfig para que
GeminiAIAnalyzer em framework/ai/ saiba:
  - qual prompt enviar ao Gemini;
  - qual schema de resposta exigir.

"""

from __future__ import annotations

from typing import Any

from framework.abstractions.abstract_ai_analysis_config import (
    AbstractAIAnalysisConfig,
)

# Vocabulário fechado de atributos visuais reconhecidos para fotos de perfil.
DATING_ATTRIBUTE_TOKENS: list[str] = [
    "lifestyle.outdoor",
    "lifestyle.homebody",
    "personality.casual",
    "personality.adventurous",
    "social.smile",
    "social.confident",
]


class DatingPhotoAnalysisConfig(AbstractAIAnalysisConfig):
    """Prompt/schema usados para analisar fotos de perfil de relacionamento."""

    def get_prompt(self) -> str:
        return (
            "Você é um assistente de um aplicativo de relacionamentos. Analise "
            "a foto de perfil e retorne uma lista de atributos de estilo de "
            "vida e personalidade percebidos (no máximo 5), escolhidos "
            "exclusivamente do vocabulário permitido pelo schema. Cada "
            "atributo deve ter 'attribute_token' e 'strength' entre 0.0 "
            "(ausente) e 1.0 (muito evidente). Não faça suposições sensíveis "
            "sobre a pessoa além do que é visualmente evidente na foto."
        )

    def get_schema(self) -> dict[str, Any]:
        return {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "attribute_token": {
                        "type": "string",
                        "enum": DATING_ATTRIBUTE_TOKENS,
                    },
                    "strength": {"type": "number"},
                },
                "required": ["attribute_token", "strength"],
            },
        }
