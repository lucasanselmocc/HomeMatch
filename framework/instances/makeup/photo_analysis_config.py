"""
framework/instances/makeup/photo_analysis_config.py
─────────────────────────────────────────────────────
Instância Makeup: configuração de análise visual por IA.

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

# Vocabulário fechado de atributos visuais reconhecidos para produtos de maquiagem.
MAKEUP_ATTRIBUTE_TOKENS: list[str] = [
    "finish.glow",
    "finish.matte",
    "finish.natural",
    "texture.creamy",
    "texture.powdery",
    "color.warm",
    "color.cool",
]


class MakeupPhotoAnalysisConfig(AbstractAIAnalysisConfig):
    """Prompt/schema usados para analisar fotos de produtos de maquiagem."""

    def get_prompt(self) -> str:
        return (
            "Você é um especialista em produtos de maquiagem. Analise a foto "
            "do produto e retorne uma lista de atributos visuais valorados "
            "(no máximo 5), escolhidos exclusivamente do vocabulário permitido "
            "pelo schema. Cada atributo deve ter 'attribute_token' e "
            "'strength' entre 0.0 (ausente) e 1.0 (muito evidente)."
        )

    def get_schema(self) -> dict[str, Any]:
        return {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "attribute_token": {
                        "type": "string",
                        "enum": MAKEUP_ATTRIBUTE_TOKENS,
                    },
                    "strength": {"type": "number"},
                },
                "required": ["attribute_token", "strength"],
            },
        }
