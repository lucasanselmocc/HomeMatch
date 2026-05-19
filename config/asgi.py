"""
ASGI config for HomeMatch project.

Esta configuração expõe a aplicação ASGI e usa o `ProtocolTypeRouter` para
direcionar requisições HTTP e WebSocket para os manipuladores apropriados.
As rotas de WebSocket são definidas em ``config.routing`` e incluem
autenticação via JWT dentro do consumidor de notificações.
"""

import os

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack

try:
    # Importa os padrões de URL WebSocket. Se não existirem, define uma lista vazia.
    from config.routing import websocket_urlpatterns
except Exception:
    websocket_urlpatterns = []

# Define o módulo de configurações padrão para o Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

# Aplicação ASGI padrão do Django para lidar com requisições HTTP
django_asgi_app = get_asgi_application()

# Compor a aplicação ASGI com suporte a HTTP e WebSocket
application = ProtocolTypeRouter(
    {
        "http": django_asgi_app,
        "websocket": AuthMiddlewareStack(URLRouter(websocket_urlpatterns)),
    }
)