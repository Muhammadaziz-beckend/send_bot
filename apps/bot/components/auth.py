import requests
from rest_framework.response import Response
from django.conf import settings

from utils.kod_generator import generate_auth_code


def telegram_auth(request):
    code = generate_auth_code()
    