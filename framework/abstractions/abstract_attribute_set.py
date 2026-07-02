"""
framework/abstract_attribute_set.py
────────────────────────────────────
Ponto flexível 1: define o conjunto de atributos/tipificadores da instância.

O usuário do framework DEVE estender esta classe e implementar:
  - getTokens()   → lista de tokens válidos para esta aplicação
  - validate()    → True se um token pertence ao conjunto
  - getDefaultSet() → subconjunto padrão de tokens

PONTO FIXO: o mecanismo de validação e filtragem de tokens inválidos na
            camada de parsing (AiAttributeParser) usa VALID_TOKENS gerado
            a partir do conjunto retornado por getTokens(). Não precisa
            ser reimplementado.
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import List


class AbstractAttributeSet(ABC):
    """
    Contrato que toda instância do HomeMatch deve implementar para definir
    o vocabulário de atributos/tipificadores da sua aplicação.
    """

    @abstractmethod
    def getTokens(self) -> List[str]:
        """
        Retorna a lista completa de tokens de atributos válidos.
        Convenção de nomenclatura: <categoria>.<folha>  ou
                                   <categoria>.<subcategoria>.<folha>
        Exemplo imobiliário: 'aesthetics.color.brightness'
        Exemplo encontros:   'interests.sports'
        """
        raise NotImplementedError

    @abstractmethod
    def validate(self, token: str) -> bool:
        """
        Verifica se um token pertence ao conjunto desta instância.
        Usado pela camada de parsing para filtrar tokens desconhecidos.
        """
        raise NotImplementedError

    @abstractmethod
    def getDefaultSet(self) -> List[str]:
        """
        Retorna o subconjunto padrão de tokens que a análise de IA
        deve produzir quando nenhuma instrução específica for dada.
        """
        raise NotImplementedError

    # ── helper concreto (ponto fixo) ─────────────────────────────────────────
    def asValidTokensFrozenset(self) -> frozenset:
        """Converte getTokens() em frozenset para lookups O(1)."""
        return frozenset(self.getTokens())
