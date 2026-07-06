"""
framework/search/nl_query_interpreter.py
───────────────────────────────────────
Interpretador genérico de consultas em linguagem natural.
"""

from __future__ import annotations


class NLQueryInterpreter:
    """
    Interpretador fixo e genérico do framework.

    Por padrão, o framework não conhece os campos específicos de cada domínio.
    Portanto, ele apenas normaliza a query e retorna um dicionário básico.

    Instâncias concretas podem sobrescrever essa classe futuramente caso
    precisem de interpretação estruturada mais específica.
    """

    def interpret(self, query: str) -> dict:
        """
        Interpreta uma consulta textual em filtros genéricos.
        """
        query = (query or "").strip()

        return {
            "raw_query": query,
            "tokens": self._tokenize(query),
        }

    def _tokenize(self, query: str) -> list[str]:
        """
        Divide a consulta em tokens simples.
        """
        return [
            token.strip().lower()
            for token in query.split()
            if token.strip()
        ]