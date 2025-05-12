from django.db import models
from django.contrib.auth.models import AbstractUser
from .managers import UserManager

from django.core.files.storage import FileSystemStorage
avatar_storage = FileSystemStorage(location='media/avatars')
class User(AbstractUser):
    ROLE_CHOICE = (
        ('admin', 'Admin'),
        ('manager', 'Manager'),
        ('user', 'User'),
    )

    email = models.EmailField(unique=True, blank=True, null=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICE, default='user')
    confirmation_code = models.CharField(max_length=6, blank=True, null=True)
    telegram_id = models.BigIntegerField(null=True, blank=True, unique=True)
    is_verified = models.BooleanField(default=False)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True, storage=avatar_storage , default = "avatars/default.jpg")
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ["username"]

    objects = UserManager()

    def save(self, *args, **kwargs):
        if not self.username and self.telegram_id:
            self.username = self.first_name
        elif not self.first_name and self.username:
            self.first_name = self.username

        super(User, self).save(*args, **kwargs)

    def __str__(self):
        return self.first_name or str(self.telegram_id) or "User"
