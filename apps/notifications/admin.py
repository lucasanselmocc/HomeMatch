"""Admin para o modelo Notification."""

from django.contrib import admin

from .models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):  # noqa: D401
    """Configuração do admin para o modelo Notification."""

    list_display = ("user", "type", "read", "created_at")
    list_filter = ("type", "read")
    search_fields = ("message", "user__email")