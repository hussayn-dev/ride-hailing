from django.conf import settings
from django.contrib.auth import authenticate
from django.utils.crypto import get_random_string
from django.utils.translation import gettext_lazy as _
from email_validator import EmailNotValidError, validate_email
from rest_framework import exceptions, serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from user.models import Token, User
from user.tasks import send_registration_email
from user.utils import generate_token


class UserMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "firstname", "lastname", "email"]


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "firstname",
            "lastname",
            "email",
            "role",
            "image",
            "verified",
            "last_login",
            "created_at",
        ]


class CreateUserSerializer(serializers.ModelSerializer):
    """Serializer for user object"""

    class Meta:
        model = User
        fields = ("id", "firstname", "lastname", "email", "phone", "role")

    def validate(self, attrs):
        email = attrs.get("email", None)
        if email:
            email = attrs["email"].lower().strip()
            if User.objects.filter(email=email).exists():
                raise serializers.ValidationError("Email already exists")
            try:
                validated_email = validate_email(attrs["email"])
                attrs["email"] = validated_email.normalized
                return super().validate(attrs)
            except EmailNotValidError as e:
                raise serializers.ValidationError(e)
        return super().validate(attrs)

    def create(self, validated_data):
        user = User.objects.create_user(
            **validated_data, password=get_random_string(10)
        )
        token_str = generate_token(user)
        token, _ = Token.objects.update_or_create(
            user=user,
            token_type="CreateToken",
            defaults={"user": user, "token_type": "CreateToken", "token": token_str},
        )

        user_data = {
            "id": user.id,
            "email": user.email,
            "fullname": "Team Member",
            "url": f"{settings.CLIENT_URL}/verify-user/?token={token.token}",
        }
        send_registration_email.delay(user_data)
        return user

    def update(self, instance, validated_data):
        # user = self.context['request'].user
        return super().update(instance, validated_data)


class CustomObtainTokenPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        if not user.verified:
            raise exceptions.AuthenticationFailed(
                _("Account not yet verified."), code="authentication"
            )
        token = super().get_token(user)
        # Add custom claims
        token.id = user.id
        token["email"] = user.email
        token["role"] = user.role
        token["fullname"] = user.fullname
        token["phone"] = user.phone
        user.save_last_login()
        return token


class AuthTokenSerializer(serializers.Serializer):
    """Serializer for user authentication object"""

    email = serializers.CharField()
    password = serializers.CharField(
        style={"input_type": "password"}, trim_whitespace=False
    )

    def validate(self, attrs):
        """Validate and authenticate the user"""
        email = attrs.get("email")
        password = attrs.get("password")

        if email:
            user = authenticate(
                request=self.context.get("request"),
                username=email.lower().strip(),
                password=password,
            )

            if not user:
                msg = _("Unable to authenticate with provided credentials")
                raise serializers.ValidationError(msg, code="authentication")
            attrs["user"] = user
        return attrs


class VerifyTokenSerializer(serializers.Serializer):
    """Serializer for token verification"""

    token = serializers.CharField(required=True)


class InitPasswordResetSerializer(serializers.Serializer):
    """Serializer for sending password reset email to the user"""

    email = serializers.CharField(required=True)


class CreatePasswordSerializer(serializers.Serializer):
    """Serializer for creating password for a new user"""

    token = serializers.CharField(required=True, write_only=True)
    password = serializers.CharField(required=True)


class PinSerializer(serializers.Serializer):
    pin = serializers.CharField(required=True)


class TokenDecodeSerializer(serializers.Serializer):
    token = serializers.CharField(required=True)
