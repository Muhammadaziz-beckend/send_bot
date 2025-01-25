import asyncio
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.conf import settings
from telethon import TelegramClient
from rest_framework.views import APIView
from .serializers import RegisterSerializer, VerificationCodeSerializer
from utils.kod_generator import generate_auth_code
from .models import User, VerificationCode

# Telegram настройки
api_id = settings.API_ID
api_hash = settings.API_HASH
phone_number = settings.PHONE


class Register(APIView):
    serializer_class = RegisterSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)

        phone = serializer.validated_data["phone"]

        if not phone:
            return Response({"error": "Телефон номер не был передан"}, status=400)

        # Проверяем наличие пользователя
        user = User.objects.filter(phone=phone).first()
        if not user:
            # Если пользователя нет, создаем нового
            user = serializer.save()

        
        verification = VerificationCode(
            owner=user,
            code=VerificationCode.generate_code(),
        )
        verification.save()

        cod = verification.code

        try:
            # Создаем event loop
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            # Инициализация клиента Telegram
            client = TelegramClient(
                f"session/admin/{str(phone_number)+str(api_id)}", api_id, api_hash, loop=loop
            )

            async def process_telegram():
                # Подключаемся к Telegram
                await client.connect()

                # Если пользователь не авторизован, отправляем запрос кода
                if not await client.is_user_authorized():
                    await client.send_code_request(phone_number)

                    # Ввод кода подтверждения администратором
                    code = input("Введите код подтверждения: ")
                    await client.sign_in(phone_number, code)

                # Отправляем сообщение пользователю
                await client.send_message(phone, f"Ваш код для подтверждения: {cod}")
                await client.disconnect()

            # Запускаем всю логику в event loop
            loop.run_until_complete(process_telegram())
            return Response(
                {"message": f"Код подтверждения отправлен на номер {phone}"}, status=200
            )

        except Exception as e:
            return Response({"error": str(e)}, status=500)

        finally:
            # Закрываем event loop корректно
            loop.close()



class ValidateCodeAPIView(APIView):
    queryset = User.objects.all()

    def post(self, request, *args, **kwargs):
        data = request.data
        phone = data.get("phone")
        code = data.get("code")

        if not phone and not code:
            return Response({"error": "Укажите телефон и код"}, status=400)

        # if phone in verification_code:
        #     if verification_code[phone] == code:
        #         return Response({"message": "Вы успешно зарегистрировались!"})
        #     else:
        #         return Response({"error": "Неверный код!"}, status=400)
        # else:
        return Response({"error": "Вы не прошли регистрацию!"}, status=400)
