from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model
from django.conf import settings
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import RegisterSerializer, ConfirmEmailSerializer, ResetPasswordSerializer, ResetPasswordConfirmSerializer
import hashlib
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAuthenticatedOrReadOnly
from rest_framework import generics, permissions
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import json
from .serializers import *
from rest_framework.decorators import api_view
from django.contrib.auth import authenticate
import threading
from django.core.files.base import ContentFile
import hashlib
import hmac
import time
import requests
from django.core.files.storage import default_storage
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.conf import settings

def verify_telegram_data(data):
    if not data or "hash" not in data:
        return False

    auth_data = {k: v for k, v in data.items() if k != "hash"}  
    check_string = "\n".join(f"{k}={v}" for k, v in sorted(auth_data.items()))

    secret_key = hashlib.sha256(settings.TELEGRAM_BOT_TOKEN.encode()).digest()
    calculated_hash = hmac.new(secret_key, check_string.encode(), hashlib.sha256).hexdigest()

    
    if not hmac.compare_digest(calculated_hash, data["hash"]):
        return False

 
    if int(time.time()) - int(data.get("auth_date", 0)) > 86400:
        return False

    return True

def download_avatar(photo_url, telegram_id, user):
    try:
        response = requests.get(photo_url)
        if response.status_code == 200:
            avatar_name = f"avatars/{telegram_id}_avatar.jpg"
            avatar_content = ContentFile(response.content)
            avatar_path = default_storage.save(avatar_name, avatar_content)
            user.avatar = avatar_path
            user.save()
    except Exception as e:
        print(f"Ошибка загрузки аватара: {e}")

@api_view(["POST", "GET"]) 
def telegram_auth(request):
    if request.method == "GET":
      
        data = request.GET.dict()  
    else:
        data = request.data

    print("Полученные данные от Telegram:", data) 

    if not verify_telegram_data(data):
        return Response({"error": "Invalid Telegram signature"}, status=403)

    telegram_id = data.get("id")
    username = data.get("username", f"tg_{telegram_id}")
    first_name = data.get("first_name", "")
    last_name = data.get("last_name", "")
    avatar_url = data.get("photo_url", None)

    if not telegram_id:
        return Response({"error": "Telegram ID is required"}, status=400)

    user, created = User.objects.get_or_create(
        telegram_id=telegram_id,
        defaults={"username": username, "first_name": first_name, "last_name": last_name},
    )

    if not created:
        user.username = username
        user.first_name = first_name
        user.last_name = last_name
        user.save()

    if avatar_url:
        threading.Thread(target=download_avatar, args=(avatar_url, telegram_id, user)).start()

    refresh = RefreshToken.for_user(user)

    return Response({
        "message": "Authenticated successfully",
        "created": created,
        "access": str(refresh.access_token),
        "refresh": str(refresh)
    })
class ProfileView(generics.RetrieveAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        user = User.objects.filter(
            pk=self.request.user.pk
        ).annotate(
            response_total_annotated=Count('forms__responses')
        ).first()
        return user

    def get_serializer_context(self):
        return {'request': self.request}

class RegisterView(APIView):
    permission_classes = [AllowAny]  

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()

          
            avatar = request.data.get("avatar")
            if avatar:
                avatar_name = f"{user.id}_avatar.jpg"
                avatar_content = ContentFile(avatar)
                avatar_path = default_storage.save(f"avatars/{avatar_name}", avatar_content)
                user.avatar = avatar_path
                user.save()

            return Response({"message": "Регистрация успешна. Код отправлен на email."}, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


from rest_framework.permissions import AllowAny


class ConfirmEmailView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        serializer = ConfirmEmailSerializer(data=request.data)
        if serializer.is_valid():
            user = User.objects.get(email=request.data['email'])
            user.is_active = True
            user.is_verified = True
            user.save()
            return Response({"message": "Email confirmed"}, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ResetPasswordView(APIView):
    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        if serializer.is_valid():
            return Response({"message": "Код подтверждения отправлен на email"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ResetPasswordConfirmView(APIView):
    def post(self, request):
        serializer = ResetPasswordConfirmSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Пароль успешно изменен"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)