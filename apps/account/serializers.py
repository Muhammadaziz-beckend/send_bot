from rest_framework import serializers
from .models import User
from django.contrib.auth.password_validation import validate_password
from django.utils.translation import gettext_lazy as _
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate

# class RegisterSerializer(serializers.ModelSerializer):

#     class Meta:
#         model = User
#         fields = (
#             "phone",
#             "store",
#             "first_name",
#             "last_name",
#             "password",
#         )

#     def validate_password(self, value):
#         try:
#             validate_password(value)
#         except serializers.ValidationError as e:
#             raise serializers.ValidationError({"password": e.messages})
#         return value


class RegisterPhoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("phone",)

# RegisterPhoneSerializer().validated_data["phone"]
# .is_valid(raise_exception=True)

    # def create(self, validated_data):
    #     user = User.objects.create_user(
    #         phone=validated_data["phone"],
    #         store=validated_data["store"],
    #         password=validated_data["password"],
    #         first_name=validated_data.get("first_name", ""),
    #         last_name=validated_data.get("last_name", ""),
    #     )
    #     return user


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