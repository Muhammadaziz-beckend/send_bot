from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from .models import *


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = (
        "id",
        "phone",
        "get_full_name",
        "get_avatar",
    )
    list_display_links = (
        "id",
        "phone",
    )
    search_fields = ("first_name", "last_name", "username")
    filter_horizontal = ("groups", "user_permissions")
    list_filter = ("is_staff", "is_superuser", "is_active", "groups")
    ordering = ("-date_joined",)

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "phone",
                    "password",
                    "telegram_id",
                    "api_hash",
                )
            },
        ),
        (
            _("Personal info"),
            {
                "fields": (
                    "avatar",
                    "get_avatar",
                    "first_name",
                    "last_name",
                )
            },
        ),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        (
            _("Important dates"),
            {
                "fields": (
                    "date_joined",
                    "last_login",
                )
            },
        ),
    )
    readonly_fields = (
        "get_full_name",
        "get_avatar",
        "date_joined",
        "last_login",
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "phone",
                    "password1",
                    "password2",
                ),
            },
        ),
    )

    @admin.display(description=_("Аватарка"))
    def get_avatar(self, user):
        if user.avatar:
            return mark_safe(
                f'<img src="{user.avatar.url}" alt="{user.get_full_name}" width="100px" />'
            )
        return "-"


@admin.register(VerificationCode)
class VerificationCodeAdmin(admin.ModelAdmin):

    list_display = (
        "owner__phone",
        "code",
        "created_at",
        "is_valid",
    )
    list_display_link = (
        "owner__phone",
        "code",
        "created_at",
        "is_valid",
    )

    list_filter = (
        "owner",
    )
