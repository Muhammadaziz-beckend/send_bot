from rest_framework import serializers
from .models import VerificationCode
from django.utils.translation import gettext_lazy as _
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password, password_changed

from .models import User


class AuthTokenSerializer(serializers.Serializer):
    phone = serializers.CharField(label=_("Phone"), write_only=True)
    password = serializers.CharField(
        label=_("Password"),
        style={"input_type": "password"},
        trim_whitespace=False,
        write_only=True,
    )
    token = serializers.CharField(label=_("Token"), read_only=True)

    def validate(self, attrs):
        phone = attrs.get("phone")
        password = attrs.get("password")

        if phone and password:
            # Аутентификация пользователя
            user = authenticate(
                request=self.context.get("request"),
                phone=phone,  # Используем phone
                password=password,
            )

            if not user:
                msg = _("Unable to log in with the provided credentials.")
                raise serializers.ValidationError(msg, code="authorization")
        else:
            msg = _('Must include "phone" and "password".')
            raise serializers.ValidationError(msg, code="authorization")

        # Проверка успешной аутентификации
        attrs["user"] = user
        return attrs

    def create(self, validated_data):
        """
        Генерация токена после успешной аутентификации.
        """
        user = validated_data["user"]
        token, created = Token.objects.get_or_create(user=user)
        return {"token": token.key}


class RegisterSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = (
            "telegram_id",
            "api_hash",
            "phone",
            "password",
        )
        extra_kwargs = {
            "telegram_id": {"required": True},
            "api_hash": {"required": True},
            "password": {"write_only": True, "required": True},
        }

    def validate_password(self, attr):
        try:
            validate_password(attr)
        except serializers.ValidationError as e:
            raise serializers.ValidationError({"password": e.messages})
        return attr

    def create(self, validated_data):
        user = User.objects.create_user(
            phone=validated_data["phone"],
            telegram_id=validated_data["telegram_id"],
            api_hash=validated_data["api_hash"],
            password=validated_data["password"],
        )
        user.save()
        return user


class VerificationCodeSerializer(serializers.ModelSerializer):

    class Meta:
        model = VerificationCode
        fields = (
            "id",
            "code",
            "owner",
            "created_at",
            "telegram_id",
        )
