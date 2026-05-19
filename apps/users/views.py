from rest_framework import viewsets, status, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import User, PropertyAlert
from .serializers import UserSerializer, RegisterSerializer, PropertyAlertSerializer
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from rest_framework.views import APIView
from django.core.mail import send_mail
from django.conf import settings
from datetime import timedelta, datetime
import jwt
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken
from .services import FavoriteService
from apps.properties.serializers.property_serializers import PropertiesReadSerializer

class RegisterUserView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = [AllowAny] 
    serializer_class = RegisterSerializer

class UserViewSet(viewsets.GenericViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get', 'patch'], url_path='me')
    def me(self, request):
        user = request.user
        
        if request.method == 'PATCH':
            serializer = self.get_serializer(user, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)
            
        serializer = self.get_serializer(user)
        return Response(serializer.data)

    # GET, POST e DELETE em /api/users/favorites/
    @action(detail=False, methods=['get', 'post', 'delete'], url_path='favorites')
    def favorites(self, request):
        user = request.user
        
        # GET: Retorna os imóveis favoritados pelo usuário
        if request.method == 'GET':
            favorites = FavoriteService.list_user_favorites(user)
            serializer = PropertiesReadSerializer(favorites, many=True)
            return Response(serializer.data)

        property_id = request.data.get('property_id')
        if not property_id:
            return Response({"error": "property_id is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        if request.method == 'POST':
            FavoriteService.add_property_to_favorites(user, property_id)
            return Response({"message": "Property added to favorites"}, status=status.HTTP_200_OK)

        elif request.method == 'DELETE':
            FavoriteService.remove_property_from_favorites(user, property_id)
            return Response({"message": "Property removed from favorites"}, status=status.HTTP_200_OK)

    # GET e POST em /api/users/alerts/
    @action(detail=False, methods=['get', 'post'], url_path='alerts')
    def alerts(self, request):
        """
        GET: Lista todos os alertas do usuário
        POST: Cria um novo alerta com os filtros fornecidos
        """
        user = request.user
        if request.method == 'GET':
            alerts_qs = PropertyAlert.objects.filter(user=user)
            serializer = PropertyAlertSerializer(alerts_qs, many=True)
            return Response(serializer.data)

        # POST: criar novo alerta
        serializer = PropertyAlertSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=user)
        return Response(
            {
                "message": "Você será avisado por email quando um imóvel com esses critérios for cadastrado",
                "alert": serializer.data,
            },
            status=status.HTTP_201_CREATED,
        )

    # DELETE em /api/users/alerts/{id}/
    @action(detail=True, methods=['delete'], url_path='alerts')
    def delete_alert(self, request, pk=None):
        """
        DELETE: Remove um alerta específico pertencente ao usuário
        """
        try:
            alert = PropertyAlert.objects.get(pk=pk, user=request.user)
            alert.delete()
            return Response({"message": "Alerta removido com sucesso"}, status=status.HTTP_204_NO_CONTENT)
        except PropertyAlert.DoesNotExist:
            return Response({"error": "Alerta não encontrado"}, status=status.HTTP_404_NOT_FOUND)

class PasswordResetRequestView(APIView):
    """
    Endpoint para solicitar redefinição de senha.
    Recebe {email}, gera um token e envia um link de redefinição por email.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        if not email:
            return Response({"error": "Email é obrigatório"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            # Retornar resposta genérica para não expor se email existe
            return Response({"message": "Se uma conta com esse email existir, um link de redefinição foi enviado."}, status=status.HTTP_200_OK)

        token_generator = PasswordResetTokenGenerator()
        token = token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        # Construir URL de redefinição
        reset_url = f"{settings.FRONTEND_URL}/password-reset-confirm/?uid={uid}&token={token}"
        # Conteúdo do email
        subject = "Redefinição de senha"
        message = (
            f"Olá {user.name},\n\n"
            "Recebemos uma solicitação para redefinir sua senha.\n"
            f"Use o link abaixo para definir uma nova senha (válido por 24h):\n\n{reset_url}\n\n"
            "Se você não solicitou, ignore este email."
        )
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )
        return Response({"message": "Se uma conta com esse email existir, um link de redefinição foi enviado."}, status=status.HTTP_200_OK)


class PasswordResetConfirmView(APIView):
    """
    Endpoint para confirmar redefinição de senha.
    Recebe {uid, token, new_password}, valida e atualiza a senha.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        uidb64 = request.data.get('uid')
        token = request.data.get('token')
        new_password = request.data.get('new_password')
        if not uidb64 or not token or not new_password:
            return Response({"error": "uid, token e new_password são obrigatórios"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return Response({"error": "Token inválido"}, status=status.HTTP_400_BAD_REQUEST)

        token_generator = PasswordResetTokenGenerator()
        if not token_generator.check_token(user, token):
            return Response({"error": "Token inválido ou expirado"}, status=status.HTTP_400_BAD_REQUEST)

        # Atualizar senha
        user.set_password(new_password)
        user.save()
        return Response({"message": "Senha atualizada com sucesso"}, status=status.HTTP_200_OK)

class EmailChangeRequestView(APIView):
    """
    Endpoint para solicitar troca de email.
    Usuário autenticado envia {new_email}, e recebe email de confirmação no novo endereço.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        new_email = request.data.get('new_email')
        if not new_email:
            return Response({"error": "new_email é obrigatório"}, status=status.HTTP_400_BAD_REQUEST)
        # Verifica se email já está em uso
        if User.objects.filter(email=new_email).exists():
            return Response({"error": "Este email já está em uso"}, status=status.HTTP_400_BAD_REQUEST)
        # Gerar token JWT com TTL de 24h
        payload = {
            'user_id': user.id,
            'new_email': new_email,
            'exp': datetime.utcnow() + timedelta(hours=24)
        }
        token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")
        # URL de confirmação (frontend irá fazer requisição para o backend)
        confirm_url = f"{settings.FRONTEND_URL}/email-change-confirm/?token={token}"
        subject = "Confirmação de troca de email"
        message = (
            f"Olá {user.name},\n\n"
            f"Você solicitou alterar seu email de acesso no HomeMatch para {new_email}.\n"
            f"Para confirmar a alteração, acesse o link abaixo (válido por 24h):\n\n{confirm_url}\n\n"
            "Se você não solicitou, ignore este email."
        )
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[new_email],
            fail_silently=False,
        )
        return Response({"message": "Um email de confirmação foi enviado para o novo endereço"}, status=status.HTTP_200_OK)


class EmailChangeConfirmView(APIView):
    """
    Endpoint para confirmar troca de email.
    Valida token e atualiza email do usuário. Invalida tokens JWT existentes.
    """
    permission_classes = [AllowAny]

    def get(self, request):
        token = request.query_params.get('token')
        if not token:
            return Response({"error": "Token é obrigatório"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            return Response({"error": "Token expirado"}, status=status.HTTP_400_BAD_REQUEST)
        except jwt.InvalidTokenError:
            return Response({"error": "Token inválido"}, status=status.HTTP_400_BAD_REQUEST)

        user_id = payload.get('user_id')
        new_email = payload.get('new_email')
        if not user_id or not new_email:
            return Response({"error": "Token inválido"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return Response({"error": "Usuário não encontrado"}, status=status.HTTP_404_NOT_FOUND)

        # Verifica se email já está em uso por outro usuário
        if User.objects.filter(email=new_email).exclude(pk=user.pk).exists():
            return Response({"error": "Email já está em uso"}, status=status.HTTP_400_BAD_REQUEST)

        # Atualiza email
        user.email = new_email
        user.save(update_fields=['email'])

        # Invalidar todos os tokens JWT existentes para o usuário
        try:
            tokens = OutstandingToken.objects.filter(user=user)
            for t in tokens:
                BlacklistedToken.objects.get_or_create(token=t)
        except Exception:
            # Caso modelos de blacklist não estejam configurados, ignore
            pass

        return Response({"message": "Email atualizado com sucesso"}, status=status.HTTP_200_OK)