from django.conf import settings
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from apps.ai_analysis.tasks import analyze_photo_task
from .models import Properties, PropertiesPhotos, Reviews
from django.utils import timezone
from apps.users.models import PropertyAlert
from apps.users.email_service import PropertyAlertEmailService
from apps.properties.filters import PropertiesFilters

# Imports para notificações em tempo real
from apps.notifications.models import Notification
from apps.notifications.serializers import NotificationSerializer
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer


# É um decorator que fica "escutando" eventos que acontecem no banco
# evento = post_delete
# sender = escuta só eventos do model Properties
@receiver(post_delete, sender=Properties)
def delete_fatherless_room(sender, instance, **kwargs):
    room = getattr(
        instance, "rooms", None
    )  # instance = o propertie que foi deletado, intance.room = pega o room que o propetie usava
    if room and not room.properties.exists():  # nenhum outro imóvel usa esse room
        room.delete()

    extras = getattr(
        instance, "rooms_extras", None
    )  # pega os extras do imóvel deletado
    if (
        extras and not extras.properties.exists()
    ):  # nenhum outro imóvel usa esses extras
        extras.delete()


@receiver(post_save, sender=PropertiesPhotos)
def trigger_ai_analysis_on_photo_upload(
    sender, instance, created, **kwargs
):  # noqa: ARG001
    """Queue LLM Vision analysis automatically whenever a new photo is saved.

    - Prompt is read from settings so it can be overridden via .env.
    """
    if not created:
        return

    prompt = getattr(settings, "AI_ANALYSIS_DEFAULT_PROMPT", "")
    if not prompt:
        return

    analyze_photo_task.delay(instance.pk, prompt)

@receiver(post_save, sender=Properties)
def check_property_alerts(sender, instance, created, **kwargs):
    """
    Signal disparado após salvar um imóvel.
    Verifica alertas ativos e notifica usuários cujos critérios casam com o novo imóvel.
    """
    # Só processa para imóveis recém-criados
    if not created:
        return

    # Buscar todos os alertas ativos
    active_alerts = PropertyAlert.objects.filter(is_active=True).select_related('user')
    for alert in active_alerts:
        # Verificar se o imóvel casa com os filtros do alerta
        if property_matches_alert(instance, alert.filters):
            # Enviar email
            success = PropertyAlertEmailService.send_property_alert_email(
                user_email=alert.user.email,
                user_name=alert.user.name,
                property_obj=instance,
                alert=alert
            )
            # Atualizar last_notified_at se email foi enviado
            if success:
                alert.last_notified_at = timezone.now()
                alert.save(update_fields=['last_notified_at'])


def property_matches_alert(property_obj, filters):
    """
    Verifica se um imóvel corresponde aos filtros de um alerta.

    Args:
        property_obj (Properties): Objeto de imóvel criado.
        filters (dict): Dicionário com os filtros do alerta.

    Returns:
        bool: True se o imóvel casa com os filtros, False caso contrário.
    """
    # Criar um queryset contendo apenas este imóvel
    queryset = Properties.objects.filter(id=property_obj.id)
    # Aplicar os filtros usando o PropertiesFilters
    filterset = PropertiesFilters(data=filters, queryset=queryset)
    # Se o queryset filtrado contém o imóvel, então ele casa com os critérios
    return queryset.filter(id__in=filterset.qs.values_list('id', flat=True)).exists()

# =========================================================================
# Sinais para notificações em tempo real
#
# Os sinais abaixo notificam usuários quando um imóvel favoritado muda de preço
# ou quando uma review é adicionada ao imóvel do proprietário. Eles criam
# registros de Notification e enviam a mensagem para o WebSocket do usuário.


def _send_realtime_notification(user, notification: Notification) -> None:
    """Helper: envia uma notificação via WebSocket para o usuário fornecido."""
    channel_layer = get_channel_layer()
    payload = NotificationSerializer(notification).data
    async_to_sync(channel_layer.group_send)(
        f"notifications_{user.id}",
        {
            "type": "send.notification",
            "notification": payload,
        },
    )


@receiver(post_save, sender=Properties)
def notify_favorite_price_update(sender, instance, created, **kwargs):  # noqa: ANN001, D401
    """Se o preço de um imóvel favoritado foi alterado, notifique os usuários."""
    if created:
        return
    # Obter estado anterior para comparar preço
    try:
        previous = sender.objects.get(pk=instance.pk)
    except sender.DoesNotExist:
        return
    # Se o preço mudou, criar notificação para todos que favoritaram
    if previous.price != instance.price:
        message = (
            f"O imóvel '{instance.address}' teve seu preço atualizado para R${instance.price}."
        )
        for user in instance.favorited_by.all():
            notification = Notification.objects.create(
                user=user,
                type=Notification.NotificationType.PRICE_UPDATE,
                message=message,
            )
            _send_realtime_notification(user, notification)


@receiver(post_save, sender=Reviews)
def notify_new_review(sender, instance, created, **kwargs):  # noqa: ANN001, D401
    """Quando uma review é criada, notifique o proprietário do imóvel."""
    if not created:
        return
    property_obj = instance.property
    owner = getattr(property_obj, "owner", None)
    if owner:
        message = f"O imóvel '{property_obj.address}' recebeu uma nova avaliação."
        notification = Notification.objects.create(
            user=owner,
            type=Notification.NotificationType.NEW_REVIEW,
            message=message,
        )
        _send_realtime_notification(owner, notification)
