from django.conf import settings
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from apps.ai_analysis.tasks import analyze_photo_task
from .models import Properties, PropertiesPhotos


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
