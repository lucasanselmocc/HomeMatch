"""
framework/instances/makeup/search_config.py
──────────────────────────────────────────
Configuração de busca natural da instância Makeup.
"""

from __future__ import annotations

from typing import Any


class MakeupSearchConfig:
    """
    Define o prompt e o schema usados pelo Gemini para interpretar
    buscas de produtos de maquiagem.
    """

    def get_prompt(self) -> str:
        return (
            "Interprete consultas de busca de produtos de maquiagem. "
            "Extraia filtros como categoria, tipo de pele, acabamento, cor "
            "e preço máximo quando estiverem presentes."
        )

    def get_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "category": {"type": ["string", "null"]},
                "skin_type": {"type": ["string", "null"]},
                "finish": {"type": ["string", "null"]},
                "color": {"type": ["string", "null"]},
                "max_price": {"type": ["number", "null"]},
            },
            "required": [
                "category",
                "skin_type",
                "finish",
                "color",
                "max_price",
            ],
        }