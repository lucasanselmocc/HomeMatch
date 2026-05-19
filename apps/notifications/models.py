"""
Modelos para o sistema de notificações em tempo real.

Cada notificação pertence a um usuário e registra o tipo do evento, uma
mensagem para exibição, se já foi lida e o instante de criação.
"""

from django.conf import settings
from django.db import models


class Notification(models.Model):
    class NotificationType(models.TextChoices):
        PRICE_UPDATE = "price_update", "Price Update"
        NEW_REVIEW = "new_review", "New Review"
        AI_ANALYSIS_COMPLETE = "ai_analysis_complete", "AI Analysis Complete"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications",
    )
    type = models.CharField(
        max_length=50,
        choices=NotificationType.choices,
    )
    message = models.TextField()
    read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "notifications"
        ordering = ["-created_at"]

    def __str__(self) -> str:  # pragma: no cover
        return f"Notification to {self.user.email}: {self.type}"
