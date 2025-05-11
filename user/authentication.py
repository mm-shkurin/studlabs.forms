from django.contrib.auth import get_user_model
from django.contrib.auth.backends import BaseBackend
User = get_user_model()

class TelegramAuthBackend(BaseBackend):
    def authenticate(self, request, telegram_id=None):
        try:
            return User.objects.get(telegram_id=telegram_id)
        except User.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
