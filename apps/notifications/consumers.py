"""
Consumidor de WebSocket para entrega de notificações em tempo real.

Os clientes devem conectar‑se em ``/ws/notifications/`` e fornecer um token
JWT válido na query string (`?token=<access_token>`). O consumidor autentica o
usuário usando o mesmo mecanismo de JWT da API REST e adiciona a conexão a um
grupo específico por usuário. Quando uma notificação é enviada para esse grupo,
ela é serializada e encaminhada ao cliente.
"""

import json
from urllib.parse import parse_qs

from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from rest_framework_simplejwt.authentication import JWTAuthentication

from .serializers import NotificationSerializer


class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):  # noqa: D401
        """Autentica o usuário via token JWT passado na query string."""
        # Extrai o token JWT da query string
        query_string = self.scope.get("query_string", b"").decode()
        params = parse_qs(query_string)
        token = params.get("token", [None])[0]
        if not token:
            await self.close()
            return

        # Autentica o usuário a partir do token
        user = await self._get_user_from_token(token)
        if user is None or not user.is_authenticated:
            await self.close()
            return

        self.user = user
        self.group_name = f"notifications_{self.user.id}"

        # Adiciona a conexão ao grupo do usuário
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, code):  # noqa: D401, ARG002
        """Remove a conexão do grupo ao desconectar."""
        if hasattr(self, "group_name"):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data=None, bytes_data=None):  # noqa: D401, ARG002
        """Ignora mensagens enviadas pelo cliente."""
        return

    async def send_notification(self, event):  # noqa: D401
        """Envia a notificação serializada de volta ao cliente."""
        notification = event.get("notification")
        if notification:
            await self.send(text_data=json.dumps(notification))

    @database_sync_to_async
    def _get_user_from_token(self, token):
        # Valida o token e retorna o usuário correspondente
        jwt_auth = JWTAuthentication()
        try:
            validated = jwt_auth.get_validated_token(token)
            return jwt_auth.get_user(validated)
        except Exception:
            return None