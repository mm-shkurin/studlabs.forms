from random import *
from django.core.mail import send_mail
from django.conf import settings
def generate_confirmation_code():
    return str(randint(100000,999999))
def send_confirmation_email(user):
    confirmation_code = generate_confirmation_code()
    user.confirmation_code = confirmation_code
    user.save(update_fields = ['confirmation_code'])
    send_mail(
        "Verification Code",
        f"Ваш код для верификации: {user.confirmation_code} "
        f"Если Вы не запрашивали этот код, возможно, кто-то пытается получить доступ к Вашему аккаунту : {user.email} . Никому не сообщайте этот код.",
        settings.EMAIL_HOST_USER,
        [user.email],
        fail_silently=False,
    )
