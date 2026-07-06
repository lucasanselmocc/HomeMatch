"""
framework/framework.py
──────────────────────
Classe principal do framework.

Responsável por receber as implementações concretas dos pontos variáveis
e montar os services fixos do framework.
"""

from __future__ import annotations

from framework.services.user_service import UserService
from framework.services.post_service import PostService
from framework.services.photo_service import PhotoService
from framework.services.analyzer_service import AnalyzerService
from framework.services.match_score_service import MatchScoreService
from framework.services.search_service import SearchService

from framework.use_cases.create_user_use_case import CreateUserUseCase
from framework.use_cases.update_user_use_case import UpdateUserUseCase
from framework.use_cases.delete_user_use_case import DeleteUserUseCase
from framework.use_cases.get_user_use_case import GetUserByEmailUseCase
from framework.use_cases.list_users_use_case import ListUsersUseCase

from framework.use_cases.create_post_use_case import CreatePostUseCase
from framework.use_cases.update_post_use_case import UpdatePostUseCase
from framework.use_cases.delete_post_use_case import DeletePostUseCase
from framework.use_cases.get_post_use_case import GetPostByIdUseCase
from framework.use_cases.list_post_use_case import ListPostsUseCase
from framework.use_cases.get_post_attributes_use_case import GetPostAttributesUseCase

from framework.use_cases.upload_photo_use_case import UploadPostPhotoUseCase
from framework.use_cases.delete_photo_use_case import DeletePostPhotoUseCase
from framework.use_cases.get_photo_use_case import GetPhotoByIdUseCase
from framework.use_cases.list_photos_use_case import ListPostPhotosUseCase

from framework.use_cases.analyze_photo_use_case import AnalyzePhotoUseCase
from framework.use_cases.analyze_post_use_case import AnalyzePostUseCase
from framework.use_cases.calc_match_score_use_case import CalculateMatchScoreUseCase
from framework.use_cases.search_post_use_case import SearchPostsUseCase


class HomeMatchFramework:
    """
    Classe principal do framework HomeMatch.

    Esta classe representa o ponto de entrada do framework. Ela recebe
    as implementações concretas fornecidas pela aplicação e monta os
    services disponíveis para uso.
    """

    def __init__(
        self,
        *,
        user_repository,
        post_repository,
        photo_repository,
        attribute_storage,
        ai_analyzer,
        match_score_strategy,
        search_pool,
    ) -> None:
        """
        Inicializa o framework com os pontos variáveis concretos.
        """

        self.user_repository = user_repository
        self.post_repository = post_repository
        self.photo_repository = photo_repository
        self.attribute_storage = attribute_storage
        self.ai_analyzer = ai_analyzer
        self.match_score_strategy = match_score_strategy
        self.search_pool = search_pool

        self.users = self._build_user_service()
        self.posts = self._build_post_service()
        self.photos = self._build_photo_service()
        self.analyzer = self._build_analyzer_service()
        self.match_score = self._build_match_score_service()
        self.search = self._build_search_service()

    def _build_user_service(self) -> UserService:
        """
        Monta o service de usuários.
        """
        return UserService(
            create_user_use_case=CreateUserUseCase(self.user_repository),
            update_user_use_case=UpdateUserUseCase(self.user_repository),
            delete_user_use_case=DeleteUserUseCase(self.user_repository),
            get_user_use_case=GetUserByEmailUseCase(self.user_repository),
            list_users_use_case=ListUsersUseCase(self.user_repository),
        )

    def _build_post_service(self) -> PostService:
        """
        Monta o service de postagens.
        """
        return PostService(
            create_post_use_case=CreatePostUseCase(self.post_repository),
            update_post_use_case=UpdatePostUseCase(self.post_repository),
            delete_post_use_case=DeletePostUseCase(self.post_repository),
            get_post_use_case=GetPostByIdUseCase(self.post_repository),
            list_post_use_case=ListPostsUseCase(self.post_repository),
            get_post_attributes_use_case=GetPostAttributesUseCase(self.attribute_storage))

    def _build_photo_service(self) -> PhotoService:
        """
        Monta o service de fotos.
        """
        return PhotoService(
            upload_photo_use_case=UploadPostPhotoUseCase(self.photo_repository),
            delete_photo_use_case=DeletePostPhotoUseCase(self.photo_repository),
            get_photo_use_case=GetPhotoByIdUseCase(self.photo_repository),
            list_photos_use_case=ListPostPhotosUseCase(self.photo_repository),
        )

    def _build_analyzer_service(self) -> AnalyzerService:
        """
        Monta o service de análise.
        """
        return AnalyzerService(
            analyze_photo_use_case=AnalyzePhotoUseCase(
                self.ai_analyzer,
                self.attribute_storage,
            ),
            analyze_post_use_case=AnalyzePostUseCase(
                self.ai_analyzer,
                self.attribute_storage,
            ),
        )

    def _build_match_score_service(self) -> MatchScoreService:
        """
        Monta o service de match-score.
        """
        return MatchScoreService(
            calc_match_score_use_case=CalculateMatchScoreUseCase(
                self.match_score_strategy,
            )
        )

    def _build_search_service(self) -> SearchService:
        """
        Monta o service de busca.
        """
        return SearchService(
            search_post_use_case=SearchPostsUseCase(
                self.post_repository,
                self.search_pool,
            )
        )
