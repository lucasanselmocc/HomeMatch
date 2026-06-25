"""
framework/abstract_search_pool.py
───────────────────────────────────
Ponto flexível 5: define quais atributos fazem parte da busca por linguagem
natural e como o ranking dos resultados é feito.

O usuário do framework DEVE estender esta classe para:
  - declarar quais tokens entram no índice de busca (getSearchableAttrs)
  - implementar o ranking (rank)
  - persistir o estado de busca se necessário (persist)

PONTO FIXO: EmbeddingService (geração e cosseno) e NLQueryInterpreter
            (parse de linguagem natural) são fornecidos pelo framework.
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any, List


class AbstractSearchPool(ABC):
    """
    Contrato para o pool de busca por linguagem natural de uma instância.
    """

    @abstractmethod
    def getSearchableAttrs(self) -> List[str]:
        """
        Retorna os tokens de atributos que devem ser indexados para busca.
        Subconjunto (ou total) dos tokens de AbstractAttributeSet.getTokens().
        """
        raise NotImplementedError

    @abstractmethod
    def rank(self, query: str, posts: List[Any]) -> List[Any]:
        """
        Ordena *posts* por relevância para a *query* textual.

        :param query:  texto livre do usuário
        :param posts:  queryset/lista de postagens pré-filtradas
        :return:       lista ordenada (mais relevante primeiro)
        """
        raise NotImplementedError

    def persist(self, results: List[Any]) -> None:
        """
        Persiste resultados de busca (ex: log de buscas, cache).
        Implementação padrão é no-op; sobrescreva se necessário.
        """
        pass  # no-op por padrão — ponto flexível opcional
