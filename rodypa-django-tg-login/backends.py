from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.http import HttpRequest


class TelegramIDBackend(ModelBackend):
    def authenticate(
            request: HttpRequest,
            telegram_id: str | None,
    ):
        UserModel = get_user_model()
        try:
            user = UserModel.objects.get(tg_id=telegram_id)
            return user
        except UserModel.DoesNotExist:
            return None
