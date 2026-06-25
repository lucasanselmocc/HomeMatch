"""
framework/use_cases/analyze_post_use_case.py
────────────────────────────────────────────
Use case fixo do framework responsável por orquestrar a análise de uma postagem.

Fluxo fixo:
  1. Recebe uma postagem e um prompt
  2. Usa um AbstractAIAnalyzer para analisar as fotos da postagem
  3. Usa um AbstractAttributeStorage para persistir os atributos gerados
  4. Recalcula os atributos agregados da postagem

Pontos flexíveis usados:
  - AbstractAIAnalyzer
  - AbstractAttributeStorage
"""

from __future__ import annotations

from typing import Any, Dict, List

from framework.abstract_ai_analyzer import AbstractAIAnalyzer
from framework.abstract_attribute_storage import AbstractAttributeStorage


class AnalyzePostUseCase:
    """
    Caso de uso fixo para análise de postagens.

    O framework controla a orquestração do processo.
    A instância concreta define:
      - como analisar uma foto;
      - como persistir os atributos resultantes.
    """

    def __init__(
        self,
        analyzer: AbstractAIAnalyzer,
        attribute_storage: AbstractAttributeStorage,
    ) -> None:
        self.analyzer = analyzer
        self.attribute_storage = attribute_storage

    def execute(self, *, post: Any, prompt: str) -> List[Dict[str, Any]]:
        """
        Analisa todas as fotos de uma postagem e persiste os atributos gerados.

        :param post: postagem a ser analisada
        :param prompt: instrução enviada ao analisador de IA
        :return: lista de resultados por foto
        """
        self._validate_input(post=post, prompt=prompt)

        results = self.analyzer.analyze_post(post, prompt)

        for result in results:
            photo_id = result.get("photo_id")
            attributes = result.get("attributes", [])

            if photo_id is None or not attributes:
                continue

            photo = post.photos.get(pk=photo_id)

            self.attribute_storage.save_photo_attributes(
                photo=photo,
                attributes=attributes,
            )

        self.attribute_storage.refresh_post_aggregates(post)

        return results

    def _validate_input(self, *, post: Any, prompt: str) -> None:
        """
        Valida os dados mínimos necessários para analisar uma postagem.
        """
        if post is None:
            raise ValueError("A postagem é obrigatória.")

        if not prompt or not prompt.strip():
            raise ValueError("O prompt de análise é obrigatório.")