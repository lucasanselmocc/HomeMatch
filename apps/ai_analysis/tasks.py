import logging

from celery import shared_task
from django.conf import settings

logger = logging.getLogger(__name__)


@shared_task
def debug_task():
    logger.info("Celery worker esta funcionando!")
    return "ok"


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 3},
)
def analyze_photo_task(self, photo_id, prompt=None):
    from apps.ai_analysis.services import AiAnalysisService
    from apps.properties.models import PropertiesPhotos

    prompt = prompt or getattr(settings, "AI_ANALYSIS_DEFAULT_PROMPT", "")
    if not prompt:
        logger.info("AI analysis skipped for photo %s because no prompt was configured.", photo_id)
        return {"photo_id": photo_id, "status": "skipped", "reason": "missing_prompt"}

    photo = PropertiesPhotos.objects.select_related("property").get(pk=photo_id)
    result = AiAnalysisService().analyze_photo(photo, prompt)

    logger.info(
        "AI analysis completed for photo %s (property %s) with %s attributes.",
        photo.id,
        photo.property_id,
        len(result),
    )
    # Notificar o proprietário que a análise foi concluída
    try:
        from apps.notifications.models import Notification
        from apps.notifications.serializers import NotificationSerializer
        from asgiref.sync import async_to_sync
        from channels.layers import get_channel_layer

        property_obj = photo.property
        owner = getattr(property_obj, "owner", None)
        if owner:
            message = f"A análise de IA do imóvel '{property_obj.address}' foi concluída."
            notification = Notification.objects.create(
                user=owner,
                type=Notification.NotificationType.AI_ANALYSIS_COMPLETE,
                message=message,
            )
            channel_layer = get_channel_layer()
            payload = NotificationSerializer(notification).data
            async_to_sync(channel_layer.group_send)(
                f"notifications_{owner.id}",
                {
                    "type": "send.notification",
                    "notification": payload,
                },
            )
    except Exception as exc:
        logger.warning("Falha ao enviar notificação de IA: %s", exc)
    return {
        "photo_id": photo.id,
        "property_id": photo.property_id,
        "status": "completed",
        "attribute_count": len(result),
    }


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 3},
)
def analyze_property_task(self, property_id, prompt=None):
    from apps.ai_analysis.services import AiAnalysisService
    from apps.properties.models import Properties

    prompt = prompt or getattr(settings, "AI_ANALYSIS_DEFAULT_PROMPT", "")
    if not prompt:
        logger.info(
            "AI analysis skipped for property %s because no prompt was configured.",
            property_id,
        )
        return {"property_id": property_id, "status": "skipped", "reason": "missing_prompt"}

    property_obj = Properties.objects.prefetch_related("photos").get(pk=property_id)
    result = AiAnalysisService().analyze_property(property_obj, prompt)

    logger.info(
        "AI analysis completed for property %s across %s photos.",
        property_obj.id,
        len(result),
    )
    return {
        "property_id": property_obj.id,
        "status": "completed",
        "photo_count": len(result),
    }
