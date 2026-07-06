"""
framework/search/gemini_query_interpreter.py
───────────────────────────────────────────
Interpretador padrão do framework para busca por linguagem natural usando Gemini.
"""

from __future__ import annotations

import json
from typing import Any

from framework.abstractions.abstract_query_interpreter import AbstractQueryInterpreter
from framework.ai.gemini_client import GeminiClient


class GeminiQueryInterpreter(AbstractQueryInterpreter):
    def __init__(
        self,
        *,
        prompt: str,
        schema: dict[str, Any],
        client: GeminiClient | None = None,
    ) -> None:
        self.prompt = prompt
        self.schema = schema
        self.client = client or GeminiClient()

    def interpret(self, query: str) -> dict[str, Any]:
        final_prompt = (
            f"{self.prompt}\n\n"
            f"Schema esperado:\n{json.dumps(self.schema, ensure_ascii=False)}\n\n"
            f"Consulta do usuário: {query}\n\n"
            "Retorne apenas um JSON válido. Não escreva explicações."
        )

        response = self.client.model.generate_content(
            final_prompt,
            generation_config={
                "response_mime_type": "application/json",
            },
        )

        return self._parse_response(response.text)

    def _parse_response(self, raw_response: str) -> dict[str, Any]:
        data = json.loads(raw_response)

        if not isinstance(data, dict):
            raise ValueError("A interpretação da busca deve retornar um objeto JSON.")

        return data