from rest_framework import serializers
from django.contrib.auth import get_user_model
from .services import generate_confirmation_code, send_confirmation_email
from forms.models import *
from .models import *
from django.urls import reverse
from user.models import User  
from django.db.models import Count,Q



class UserProfileFormSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()
    response_count = serializers.SerializerMethodField()  # Изменено на метод для ясности

    class Meta:
        model = Form
        fields = ['id', 'title', 'description', 'creat_time', 'response_count', 'url']
    
    def get_url(self, obj):
        request = self.context.get('request')
        if request:
            return request.build_absolute_uri(
                reverse('form-detail', kwargs={'pk': obj.id}))
        return None
    
    def get_response_count(self, obj):
        # Количество уникальных ответов на форму
        return obj.responses.count()
class ProfileSerializer(serializers.ModelSerializer):
    forms = serializers.SerializerMethodField()
    form_count = serializers.SerializerMethodField()
    response_total = serializers.SerializerMethodField()
    
    class Meta: 
        model = User
        fields = ['username', 'avatar', 'forms', 'form_count', 'response_total']
    
    def get_forms(self, obj):
        forms = obj.forms.annotate(
            response_count=Count('responses')
        ).order_by('-creat_time')
        
        return UserProfileFormSerializer(
            forms,
            many=True,
            context=self.context
        ).data
    
    def get_form_count(self, obj):
        return obj.forms.count()
    
    def get_response_total(self, obj):
        return Response.objects.filter(form__owner=obj).count()
    

class TelegramAuthSerializer(serializers.Serializer):
    telegram_id = serializers.IntegerField()

    def validate(self, data):
        telegram_id = data.get("telegram_id")

    

        if telegram_id is None:
            raise serializers.ValidationError("Telegram ID обязателен.")

       
        if not isinstance(telegram_id, int):
            raise serializers.ValidationError("Telegram ID должен быть числом.")

        try:
            user = User.objects.get(telegram_id=telegram_id)
        except User.DoesNotExist:
            raise serializers.ValidationError("Пользователь не найден.")

        return {"user": user}
    
class RegisterSerializer(serializers.ModelSerializer):
    password_confirm = serializers.CharField(write_only=True)
    telegram_id = serializers.IntegerField(required=False, allow_null=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'password_confirm', 'role', 'telegram_id')

    def validate(self, data):
        if 'telegram_id' not in data and ('email' not in data or not data['email']):
            raise serializers.ValidationError("Необходимо указать email или Telegram ID.")

        if 'password' in data and 'password_confirm' in data and data['password'] != data['password_confirm']:
            raise serializers.ValidationError("Пароли не совпадают.")

        if 'telegram_id' in data and data['telegram_id']:
            if User.objects.filter(telegram_id=data['telegram_id']).exists():
                raise serializers.ValidationError("Этот Telegram ID уже зарегистрирован.")

        return data

    def create(self, validated_data):
        validated_data.pop('password_confirm', None)
        user = User.objects.create_user(**validated_data, is_active=False)

        if user.email:
            user.confirmation_code = generate_confirmation_code()
            user.save()
            send_confirmation_email(user)

        return user




class ConfirmEmailSerializer(serializers.Serializer):
    email = serializers.EmailField()
    confirmation_code = serializers.CharField(max_length=6)

    def validate(self, data):
        try:
            user = User.objects.get(email=data['email'])
        except User.DoesNotExist:
            raise serializers.ValidationError("Пользователь не найден.")

        if user.confirmation_code != data['confirmation_code']:
            raise serializers.ValidationError("Неверный код подтверждения.")

        return data

    def save(self):
        user = User.objects.get(email=self.validated_data['email'])
        user.confirmation_code = None
        user.save()


class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        try:
            user = User.objects.get(email=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("Пользователь с таким email не найден.")

        confirmation_code = generate_confirmation_code()
        user.confirmation_code = confirmation_code
        user.save()
        send_confirmation_email(user)
        return value


class ResetPasswordConfirmSerializer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.CharField(max_length=6)
    new_password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    def validate(self, data):
        try:
            user = User.objects.get(email=data['email'])
        except User.DoesNotExist:
            raise serializers.ValidationError("Пользователь не найден.")

        if user.confirmation_code != data['code']:
            raise serializers.ValidationError("Неверный код подтверждения.")

        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError("Пароли не совпадают.")

        return data

    def save(self):
        user = User.objects.get(email=self.validated_data['email'])
        user.set_password(self.validated_data['new_password'])
        user.confirmation_code = None
        user.save() 