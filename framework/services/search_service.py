"""
framework/services/search_service.py
───────────────────────────────────
Service fixo do framework responsável por agrupar os casos de uso
relacionados à busca de postagens.

A estratégia concreta de busca é fornecida pela aplicação que
utiliza o framework.
"""

from __future__ import annotations

from framework.use_cases.search_post_use_case import SearchPostsUseCase


class SearchService:
    """
    Service responsável pelas operações de busca.

    Esta classe encapsula o caso de uso responsável pela busca
    de postagens utilizando linguagem natural.
    """

    def __init__(
        self,
        search_post_use_case: SearchPostsUseCase,
    ) -> None:
        """
        Inicializa o service com o caso de uso necessário.
        """
        self.search_post_use_case = search_post_use_case

    def search_posts(self, **kwargs):
        """
        Realiza a busca de postagens.
        """
        return self.search_post_use_case.execute(**kwargs)
