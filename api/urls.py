from django.urls import path, include
from rest_framework.routers import DefaultRouter

from apps.account.views import Register

from .ysge import swagger

router = DefaultRouter()

urlpatterns = [
    path("auth/register/", Register.as_view()),
    #
    path("", include(router.urls)),
]

urlpatterns += swagger
