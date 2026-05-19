"""
Define rotas para WebSocket da aplicação HomeMatch.

Atualmente, existe apenas uma rota que aceita conexões em ``/ws/notifications/``
e delega ao ``NotificationConsumer``, que lida com autenticação via JWT e
entrega de notificações em tempo real para cada usuário.
"""

from django.urls import re_path

from apps.notifications.consumers import NotificationConsumer

# Lista de padrões de URL WebSocket. O cliente deve incluir o token JWT na
# query string, por exemplo: ``/ws/notifications/?token=...``.
websocket_urlpatterns = [
    re_path(r"^ws/notifications/$", NotificationConsumer.as_asgi()),
]