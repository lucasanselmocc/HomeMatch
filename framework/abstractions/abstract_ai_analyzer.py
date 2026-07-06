"""
framework/abstract_ai_analyzer.py
──────────────────────────────────
Ponto flexível 2: define o mecanismo de análise de imagens utilizado pela
instância.

O framework fornece uma implementação padrão baseada no Gemini
(GeminiAIAnalyzer), responsável por:

    • enviar a imagem para o modelo;
    • utilizar o prompt e o schema definidos pela instância;
    • interpretar a resposta.

Caso desejado, a aplicação pode fornecer outra implementação
(ex.: OpenAI, modelo local, regras heurísticas etc.).
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, List


class AbstractAIAnalyzer(ABC):
    """
    Contrato para mecanismos de análise de imagens.

    Uma implementação concreta deve apenas saber analisar
    uma foto e retornar atributos valorados.
    """

    @abstractmethod
    def analyze_photo(
        self,
        photo: Any,
        prompt: str | None = None,
    ) -> List[Dict[str, Any]]:
        """
        Analisa uma única foto.

        Retorno esperado:

        [
            {
                "attribute_token": "...",
                "strength": 0.85
            }
        ]

        O parâmetro ``prompt`` é opcional. Quando não informado,
        a implementação pode utilizar um prompt padrão definido
        por sua configuração.
        """
        raise NotImplementedError

    def analyze_post(
        self,
        post: Any,
        prompt: str | None = None,
    ) -> List[Dict[str, Any]]:
        """
        Implementação padrão: analisa todas as fotos da postagem.
        """

        results: list[dict] = []

        for photo in post.photos.all():
            attributes = self.analyze_photo(
                photo=photo,
                prompt=prompt,
            )

            results.append(
                {
                    "photo_id": photo.pk,
                    "attributes": attributes,
                }
            )

        return results