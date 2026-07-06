"""
framework/abstract_ai_analyzer.py
──────────────────────────────────
Ponto flexível 2: define a lógica de análise de imagens/fotos da instância.

O usuário do framework PODE:
  - usar o módulo padrão (AiVisionClient + AiAttributeParser) sem alterar nada, OU
  - estender esta classe para fornecer uma lógica de análise própria.

PONTO FIXO: AiVisionClient e AiAttributeParser são implementações concretas
            fornecidas pelo framework e não precisam ser reimplementadas.
            A orquestração em AiAnalysisService também é fixa.
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any, Dict, List


class AbstractAIAnalyzer(ABC):
    """
    Contrato para a camada de análise de imagens de uma instância HomeMatch.

    Uma implementação mínima precisa apenas de analyze_photo().
    analyze_post() tem uma implementação padrão que itera sobre as fotos.
    """

    @abstractmethod
    def analyze_photo(self, photo: Any, prompt: str) -> List[Dict[str, Any]]:
        """
        Analisa uma única foto e retorna lista de atributos valorados.

        Retorno esperado:
            [{"attribute_token": "interests.sports", "strength": 0.85}, ...]

        :param photo:  objeto de foto (deve ter pelo menos .pk e .post/property)
        :param prompt: instrução textual enviada ao modelo de visão
        """
        raise NotImplementedError

    def analyze_post(self, post: Any, prompt: str) -> List[Dict[str, Any]]:
        """
        Analisa todas as fotos de uma postagem.
        Implementação padrão — pode ser sobrescrita pela instância.
        """
        results: list[dict] = []
        for photo in post.photos.all():
            attributes = self.analyze_photo(photo, prompt)
            results.append({"photo_id": photo.pk, "attributes": attributes})
        return results
