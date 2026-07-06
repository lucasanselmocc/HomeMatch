"""
framework/ai/gemini_client.py
─────────────────────────────
Cliente responsável por se comunicar com a API do Gemini.
"""

from __future__ import annotations

import os
from typing import Any

import google.generativeai as genai


class GeminiClient:
    """
    Cliente concreto para chamadas ao Gemini.

    Este componente não depende de Django. A chave pode ser passada
    diretamente ou lida da variável de ambiente GEMINI_API_KEY.
    """

    def __init__(
        self,
        *,
        api_key: str | None = None,
        model: str | None = None,
    ) -> None:
        self.api_key = api_key or 'AIzaSyCqooKbJPMd4iWnROsk6gUoT0nLtDrF124'

        self.model_name = (
            model
            or os.getenv("GEMINI_MODEL")
            or "gemini-2.0-flash"
        )

        if not self.api_key:
            raise ValueError("Nenhuma chave GEMINI_API_KEY foi encontrada.")

        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(self.model_name)

    def analyze_photo(
        self,
        *,
        image: Any,
        prompt: str,
        schema: dict,
    ):
        """
        Envia uma imagem, um prompt e um schema para o Gemini.
        """
        return self.model.generate_content(
            [prompt, image],
            generation_config={
                "response_mime_type": "application/json",
                "response_schema": schema,
            },
        )