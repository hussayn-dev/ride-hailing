import logging
from datetime import datetime

import jwt
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password, make_password
from django.core.cache.backends.base import DEFAULT_TIMEOUT
from django.utils.timezone import make_aware
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from user.decorators import jwt_required
from user.models import Token, User
from user.tasks import send_password_reset_email
from user.utils import generate_token
from user.v1.serializers import (
    CreatePasswordSerializer,
    CreateUserSerializer,
    CustomObtainTokenPairSerializer,
    InitPasswordResetSerializer,
    PinSerializer,
    TokenDecodeSerializer,
    UserSerializer,
    VerifyTokenSerializer,
)

CACHE_TTL = getattr(settings, "CACHE_TTL", DEFAULT_TIMEOUT)
logger = logging.getLogger(__name__)


class DecodeJwtTokenView(APIView):
    serializer_class = TokenDecodeSerializer

    @jwt_required  # only a valid token can access this view
    def post(self, request):
        # print("META", request.META)
        # print("PAYLOAD", request.data)
        token = request.data.get("token", None)
        if token:
            try:
                payload = jwt.decode(token, settings.SECRET_KEY, algorithms="HS256")
            except jwt.ExpiredSignatureError as e:
                logger.error(e)
                raise AuthenticationFailed("Unauthenticated")

            user = User.objects.get(id=payload["user_id"])
            serializer = UserSerializer(instance=user)
            return Response(
                {
                    **serializer.data,
                    # "tenant_id": payload["id"],
                    # "permissions": user.permission_list(),
                }
            )
        raise AuthenticationFailed("Unauthenticated")


class UserVieSets(viewsets.ModelViewSet):
    """User viewsets"""

    queryset = get_user_model().objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ["get", "post", "patch", "delete"]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = [
        "is_active",
        "role",
    ]
    search_fields = ["email", "firstname", "lastname", "phone"]
    ordering_fields = [
        "created_at",
        "email",
        "firstname",
        "lastname",
    ]

    def create(self, request, *args, **kwargs):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def update(self, request, *args, **kwargs):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def get_permissions(self):
        permission_classes = self.permission_classes
        if self.action in [
            "create_password",
            "initialize_reset",
            "verify_token",
            "retrieve",
            "list",
        ]:
            permission_classes = [AllowAny]
        elif self.action in ["destroy", "partial_update"]:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    @action(
        methods=["POST"],
        detail=False,
        serializer_class=CreateUserSerializer,
        url_path="invite-user",
    )
    def invite_user(self, request, pk=None):
        """This endpoint invites new user"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {"success": True, "data": serializer.data}, status=status.HTTP_200_OK
        )

    @action(
        methods=["POST"],
        detail=False,
        serializer_class=VerifyTokenSerializer,
        url_path="verify-token",
        permission_classes=[AllowAny],
    )
    def verify_token(self, request, pk=None):
        """This endpoint verifies token"""
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            token = Token.objects.filter(token=request.data.get("token")).first()
            if token and token.is_valid():
                return Response(
                    {"success": True, "valid": True}, status=status.HTTP_200_OK
                )
            return Response(
                {"success": False, "valid": False}, status=status.HTTP_404_NOT_FOUND
            )
        return Response(
            {"success": False, "errors": serializer.errors}, status.HTTP_400_BAD_REQUEST
        )

    @action(
        methods=["POST"],
        detail=False,
        serializer_class=InitPasswordResetSerializer,
        url_path="reset-password",
        permission_classes=[AllowAny],
    )
    def initialize_reset(self, request, pk=None):
        """This endpoint initializes password reset by sending password reset email to user"""
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            email = request.data["email"].lower().strip()
            user = get_user_model().objects.filter(email=email, is_active=True).first()
            if not user:
                return Response(
                    {"success": False, "message": "user with this record not found"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            token, created = Token.objects.update_or_create(
                user=user,
                token_type="ResetToken",
                defaults={
                    "user": user,
                    "token": generate_token(user),
                    "token_type": "ResetToken",
                },
            )
            email_data = {
                "fullname": user.firstname,
                "email": user.email,
                "token": token.token,
            }
            send_password_reset_email.delay(email_data)
            return Response(
                {
                    "success": True,
                    "message": "Email successfully sent to registered email",
                },
                status=status.HTTP_200_OK,
            )
        return Response(
            {"success": False, "errors": serializer.errors}, status.HTTP_400_BAD_REQUEST
        )

    @action(
        methods=["POST"],
        detail=False,
        serializer_class=CreatePasswordSerializer,
        url_path="create-password",
    )
    def create_password(self, request, pk=None):
        """Create a new password given the reset token"""
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            token_data = data.pop("token")
            token = Token.objects.filter(token=token_data).first()
            if not token or not token.is_valid():
                return Response(
                    {"success": False, "errors": "Invalid token specified"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            user = User.objects.get(id=token.user.id)
            user.set_password(data["password"])
            if not user.verified:
                user.verified = True
                user.email_verified_at = make_aware(datetime.now())
            user.save()
            token.delete()
            return Response(
                {"success": True, "message": "Password successfully set"},
                status=status.HTTP_200_OK,
            )
        return Response(
            {"success": False, "errors": serializer.errors}, status.HTTP_400_BAD_REQUEST
        )

    @action(
        methods=["POST"],
        detail=True,
        serializer_class=PinSerializer,
        url_path="create-pin",
    )
    def create_pin(self, request, pk=None):
        user = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user.transaction_pin = make_password(serializer.validated_data["pin"])
        user.save()
        return Response(
            {"success": True, "message": "Pin set successfully"},
            status=status.HTTP_200_OK,
        )

    @action(
        methods=["POST"],
        detail=False,
        serializer_class=PinSerializer,
        url_path="verify-pin",
    )
    def verify_pin(self, request, pk=None):
        user = self.request.user
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        transaction_pin = user.transaction_pin
        is_valid = (
            check_password(serializer.validated_data["pin"], transaction_pin)
            if transaction_pin
            else False
        )
        if is_valid:
            return Response(
                {"success": True, "message": "Pin is valid"}, status=status.HTTP_200_OK
            )
        return Response(
            {"success": False, "errors": "Invalid Pin"},
            status=status.HTTP_401_UNAUTHORIZED,
        )


class CustomObtainTokenPairView(TokenObtainPairView):
    """Login with email and password"""

    serializer_class = CustomObtainTokenPairSerializer
