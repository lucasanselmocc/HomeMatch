from __future__ import annotations

from typing import Any


class MakeupAIConfig:
    def get_prompt(self) -> str:
        return (
            "Interprete consultas de busca de produtos de maquiagem. "
            "Extraia filtros como categoria, tipo de pele, acabamento, cor "
            "e preço máximo quando estiverem presentes. "
            "Quando uma informação textual não estiver presente, retorne string vazia. "
            "Quando o preço máximo não estiver presente, retorne 0."
        )

    def get_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "category": {"type": "string"},
                "skin_type": {"type": "string"},
                "finish": {"type": "string"},
                "color": {"type": "string"},
                "max_price": {"type": "number"},
            },
            "required": [
                "category",
                "skin_type",
                "finish",
                "color",
                "max_price",
            ],
        }