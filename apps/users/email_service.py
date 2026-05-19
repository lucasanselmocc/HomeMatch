from django.core.mail import send_mail
from django.conf import settings


class PropertyAlertEmailService:
    """
    Serviço para envio de emails de alertas de imóveis.
    """

    @staticmethod
    def send_property_alert_email(user_email, user_name, property_obj, alert):
        """
        Envia email notificando sobre novo imóvel que casa com os critérios do alerta.

        Args:
            user_email (str): Email do usuário
            user_name (str): Nome do usuário
            property_obj (Properties): Objeto Properties que foi criado
            alert (PropertyAlert): Objeto PropertyAlert que foi ativado

        Returns:
            bool: True se o email foi enviado com sucesso, False caso contrário.
        """
        # Construir URL do imóvel (ajustar conforme o frontend)
        property_url = f"{settings.FRONTEND_URL}/properties/{property_obj.id}"

        subject = f"🏠 Novo imóvel encontrado: {property_obj.get_type_display()} em {property_obj.neighborhood}"

        # Mensagem em texto plano (fallback)
        message = (
            f"Olá {user_name},\n\n"
            "Encontramos um novo imóvel que corresponde aos seus critérios de busca!\n\n"
            "Detalhes do imóvel:\n"
            f"- Tipo: {property_obj.get_type_display()}\n"
            f"- Localização: {property_obj.neighborhood}, {property_obj.city}\n"
            f"- Preço: R$ {property_obj.price}\n"
            f"- Área: {property_obj.area}m²\n"
            f"- Quartos: {property_obj.rooms.bedrooms}\n"
            f"- Banheiros: {property_obj.rooms.bathrooms}\n\n"
            f"Ver imóvel: {property_url}\n\n"
            "---\n"
            "Esta é uma notificação automática do sistema de alertas HomeMatch.\n"
            f"Para gerenciar seus alertas, acesse: {settings.FRONTEND_URL}/alerts\n"
        )

        try:
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user_email],
                fail_silently=False,
            )
            return True
        except Exception as e:
            print(f"Erro ao enviar email de alerta: {e}")
            return False