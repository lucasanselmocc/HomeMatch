"""
Views para listar e atualizar notificações via API REST.

Permite que um usuário autenticado veja suas notificações e marque uma
notificação como lida.
"""

from rest_framework import generics, permissions

from .models import Notification
from .serializers import NotificationSerializer


class NotificationListView(generics.ListAPIView):
    """
    Lista todas as notificações do usuário autenticado, ordenadas da mais
    recente para a mais antiga.
    """

    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user).order_by("-created_at")


class NotificationUpdateView(generics.UpdateAPIView):
    """
    Marca uma notificação como lida. Apenas o campo ``read`` deve ser
    atualizado via PATCH.
    """

    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ["patch"]

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)
