import asyncio
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.conf import settings
from telethon import TelegramClient
from rest_framework.views import APIView
from utils.kod_generator import generate_auth_code
from .models import User

# Telegram настройки
api_id = settings.API_ID
api_hash = settings.API_HASH
phone_number = settings.PHONE
verification_code = {}

class Register(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        data = request.data
        phone = data.get("phone")

        if not phone:
            return Response({"error": "Phone number is required"}, status=400)

        if phone in verification_code:
            return Response({"error": "Code already sent"}, status=400)

        # Создаем event loop
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            # Инициализация клиента
            client = TelegramClient("session_name", api_id, api_hash, loop=loop)
            cod = generate_auth_code()

            async def process_telegram():
                # Подключение и отправка сообщения
                await client.start(phone_number)
                await client.send_message(phone, f"Ваш код: {cod}")

                # Отключение клиента
                await client.disconnect()

            # Запускаем всю логику в event loop
            loop.run_until_complete(process_telegram())

            # Сохраняем код в словарь
            verification_code[phone] = cod
            return Response({"message": f"Verification code sent to {phone}"}, status=200)

        except Exception as e:
            return Response({"error": str(e)}, status=500)

        finally:
            # Закрываем loop корректно
            loop.close()

class ValidateCodeAPIView(APIView):
    queryset = User.objects.all()
    
    