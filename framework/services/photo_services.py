"""
framework/services/photo_service.py
──────────────────────────────────
Service fixo do framework responsável por agrupar os casos de uso
relacionados ao gerenciamento de fotos.

Esta classe fornece uma interface simplificada para manipular fotos
associadas às postagens.
"""

from __future__ import annotations

from framework.use_cases.delete_photo_use_case import DeletePostPhotoUseCase
from framework.use_cases.get_photo_use_case import GetPhotoByIdUseCase
from framework.use_cases.list_photos_use_case import ListPostPhotosUseCase
from framework.use_cases.upload_photo_use_case import UploadPostPhotoUseCase


class PhotoService:
    """
    Service responsável pelo gerenciamento de fotos.

    Esta classe agrupa os casos de uso responsáveis pelo upload,
    recuperação, listagem e remoção de fotos.
    """

    def __init__(
        self,
        upload_photo_use_case: UploadPostPhotoUseCase,
        delete_photo_use_case: DeletePostPhotoUseCase,
        get_photo_use_case: GetPhotoByIdUseCase,
        list_photos_use_case: ListPostPhotosUseCase,
    ) -> None:
        """
        Inicializa o service com os casos de uso necessários.
        """
        self.upload_photo_use_case = upload_photo_use_case
        self.delete_photo_use_case = delete_photo_use_case
        self.get_photo_use_case = get_photo_use_case
        self.list_photos_use_case = list_photos_use_case

    def upload_photo(self, **kwargs):
        """Realiza o upload de uma foto."""
        return self.upload_photo_use_case.execute(**kwargs)

    def delete_photo(self, **kwargs):
        """Remove uma foto."""
        return self.delete_photo_use_case.execute(**kwargs)

    def get_photo(self, **kwargs):
        """Recupera uma foto."""
        return self.get_photo_use_case.execute(**kwargs)

    def list_photos(self, **kwargs):
        """Lista as fotos associadas a uma postagem."""
        return self.list_photos_use_case.execute(**kwargs)