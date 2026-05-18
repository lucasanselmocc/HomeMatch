from rest_framework.routers import DefaultRouter
from .views import (UserViewSet, RegisterUserView, PasswordResetRequestView, PasswordResetConfirmView, EmailChangeRequestView, EmailChangeConfirmView,)
from django.urls import path
from rest_framework_simplejwt.views import (TokenObtainPairView, TokenRefreshView, TokenBlacklistView)

router = DefaultRouter()
router.register(r"", UserViewSet, basename="user")
urlpatterns = [
    path('register/', RegisterUserView.as_view(), name='register'),
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('logout/', TokenBlacklistView.as_view(), name='logout'),
    path('password-reset/', PasswordResetRequestView.as_view(), name='password_reset'),
    path('password-reset/confirm/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('email-change/', EmailChangeRequestView.as_view(), name='email_change'),
    path('email-change/confirm/', EmailChangeConfirmView.as_view(), name='email_change_confirm'),
    path('alerts/<int:pk>/', UserViewSet.as_view({'delete': 'delete_alert'}), name='alert-delete'),
] + router.urls

