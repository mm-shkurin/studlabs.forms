from django.urls import path, include
from .views import *
from django.conf import settings
from django.conf.urls.static import static
app_name = "user"

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('confirm-email/', ConfirmEmailView.as_view(), name='confirm-email'),
    path('me/', ProfileView.as_view(), name='information-of-user'),
    path('reset-password/', ResetPasswordView.as_view(), name='reset-password'),
    path('reset-password-confirm/', ResetPasswordConfirmView.as_view(), name='reset-password-confirm'),
    path('telegram/', telegram_auth, name='telegram_auth'), 
    path('auth/', include('djoser.urls')),  
    path('auth/', include('djoser.urls.jwt')),  
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)