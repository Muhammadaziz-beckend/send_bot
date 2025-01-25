import random
import string
from django.db import models
from datetime import timedelta
from .manager import UserNewManager
from django.contrib import messages
from django.utils.timezone import now
from asgiref.sync import async_to_sync
from telethon.sync import TelegramClient
from django_resized import ResizedImageField
from telethon.errors import ApiIdInvalidError, RPCError,PhoneCodeInvalidError, PhoneNumberFloodError
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractUser
from phonenumber_field.modelfields import PhoneNumberField
from django.db import transaction
import re

class User(AbstractUser):

    class Meta:
        verbose_name = "пользователь"
        verbose_name_plural = "пользователи"
        ordering = ("-date_joined",)

    phone = PhoneNumberField(
        "Телефон номер",
        unique=True,
        null=True,
        blank=True,
    )
    avatar = ResizedImageField(
        _("аватарка"),
        size=[500, 500],
        crop=["middle", "center"],
        upload_to="avatars/",
        force_format="WEBP",
        quality=90,
        null=True,
        blank=True,
    )
    telegram_id = models.CharField(
        unique=True,
        verbose_name="Telegram ID",
        null=True,
        max_length=12,
    )
    api_hash = models.CharField(
        "API hash",
        unique=True,
        max_length=160,
        null=True,
    )
    first_name = models.CharField(
        _("first name"),
        max_length=150,
    )
    last_name = models.CharField(
        _("last name"),
        max_length=150,
    )
    email = None
    username = None

    USERNAME_FIELD = "phone"
    REQUIRED_FIELDS = []

    objects = UserNewManager()

    @staticmethod
    def get_name_session(self):
        if self.phone and self.telegram_id:
            return f"{str(self.phone)+str(self.telegram_id)}"
        return

    @property
    def get_full_name(self):
        return f"{self.last_name} {self.first_name}"

    get_full_name.fget.short_description = _("полное имя")

    def __str__(self):
        return f"{str(self.phone) or self.get_full_name}"

class VerificationCode(models.Model):
    owner = models.ForeignKey(
        "account.User",
        models.CASCADE,
        null=True,
        blank=True,
        related_name="verification_codes",
        verbose_name="Владелец",
    )
    code = models.CharField(
        max_length=6,
        verbose_name="Код подтверждения",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Время создания",
    )

    def is_valid(self):
        """Проверка, не истёк ли код (например, через 5 минут)"""
        return now() < self.created_at + timedelta(minutes=5)

    @staticmethod
    def generate_code(length=6):
        """Генерация случайного кода"""
        return "".join(random.choices(string.digits, k=length))

    class Meta:
        verbose_name = "Код для подтверждения"
        verbose_name_plural = "Коды для подтверждения"
