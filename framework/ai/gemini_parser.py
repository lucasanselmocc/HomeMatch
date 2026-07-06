"""
framework/ai/gemini_parser.py
─────────────────────────────
Parser responsável por converter respostas do Gemini em atributos.
"""

from __future__ import annotations

import json
from typing import Any


class GeminiParser:
    """
    Converte respostas JSON do Gemini para lista de atributos valorados.
    """

    @staticmethod
    def extract_attributes(response: Any) -> list[dict]:
        """
        Extrai atributos da resposta retornada pelo Gemini.
        """
        raw_text = getattr(response, "text", response)

        data = json.loads(raw_text)

        if isinstance(data, list):
            return data

        if isinstance(data, dict) and "attributes" in data:
            return data["attributes"]

        if isinstance(data, dict):
            return [data]

        raise ValueError("Resposta da IA fora do formato esperado.")