"""
framework/use_cases/analyze_photo_use_case.py
─────────────────────────────────────────────
Use case fixo do framework responsável por orquestrar a análise de uma única foto.

Fluxo fixo:
  1. Recebe uma foto e um prompt
  2. Usa um AbstractAIAnalyzer para analisar a foto
  3. Usa um AbstractAttributeStorage para persistir os atributos gerados
  4. Recalcula os atributos agregados da postagem relacionada à foto
  5. Retorna os atributos extraídos

Pontos flexíveis usados:
  - AbstractAIAnalyzer
  - AbstractAttributeStorage
"""

from __future__ import annotations

from typing import Any, Dict, List

from framework.abstract_ai_analyzer import AbstractAIAnalyzer
from framework.abstract_attribute_storage import AbstractAttributeStorage


class AnalyzePhotoUseCase:
    """
    Caso de uso fixo para análise de uma única foto.

    O framework controla a orquestração do processo.
    A instância concreta define:
      - como analisar a foto;
      - como persistir os atributos resultantes.
    """

    def __init__(
        self,
        analyzer: AbstractAIAnalyzer,
        attribute_storage: AbstractAttributeStorage,
    ) -> None:
        self.analyzer = analyzer
        self.attribute_storage = attribute_storage

    def execute(self, *, photo: Any, prompt: str) -> List[Dict[str, Any]]:
        """
        Analisa uma única foto, persiste os atributos gerados e atualiza
        os agregados da postagem associada.

        :param photo: foto a ser analisada
        :param prompt: instrução enviada ao analisador de IA
        :return: lista de atributos extraídos da foto

        Retorno esperado:
            [
                {
                    "attribute_token": "livability.coziness",
                    "strength": 0.85
                },
                {
                    "attribute_token": "current_state.cleanliness",
                    "strength": 0.92
                }
            ]
        """
        self._validate_input(photo=photo, prompt=prompt)

        attributes = self.analyzer.analyze_photo(
            photo=photo,
            prompt=prompt.strip(),
        )

        self.attribute_storage.save_photo_attributes(
            photo=photo,
            attributes=attributes,
        )

        post = self._get_post_from_photo(photo)

        self.attribute_storage.refresh_post_aggregates(post)

        return attributes

    def _validate_input(self, *, photo: Any, prompt: str) -> None:
        """
        Valida os dados mínimos necessários para analisar uma foto.
        """
        if photo is None:
            raise ValueError("A foto é obrigatória.")

        if not prompt or not prompt.strip():
            raise ValueError("O prompt de análise é obrigatório.")

    def _get_post_from_photo(self, photo: Any) -> Any:
        """
        Recupera a postagem associada à foto.

        Como diferentes instâncias podem nomear essa relação de formas diferentes,
        o framework tenta nomes comuns.
        """
        if hasattr(photo, "post"):
            return photo.post

        if hasattr(photo, "property"):
            return photo.property

        raise ValueError("Não foi possível identificar a postagem associada à foto.")