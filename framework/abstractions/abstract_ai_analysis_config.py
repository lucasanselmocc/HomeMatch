"""
framework/abstractions/abstract_ai_analysis_config.py
─────────────────────────────────────────────────────
Ponto flexível: define a configuração utilizada pelo analisador de IA.

O framework é responsável por:
    • chamar o modelo de IA (ex.: Gemini);
    • enviar a imagem;
    • enviar o prompt;
    • solicitar a resposta no schema informado;
    • interpretar a resposta.

A instância apenas informa:
    • qual prompt utilizar;
    • qual schema espera receber.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class AbstractAIAnalysisConfig(ABC):
    """
    Contrato para configuração da análise de IA.
    """

    @abstractmethod
    def get_prompt(self) -> str:
        """
        Retorna o prompt que será enviado ao modelo de IA.
        """
        raise NotImplementedError

    @abstractmethod
    def get_schema(self) -> dict[str, Any]:
        """
        Retorna o JSON Schema esperado para a resposta da IA.

        O framework utilizará esse schema para solicitar uma
        resposta estruturada ao modelo.
        """
        raise NotImplementedError