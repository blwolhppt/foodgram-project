from django.contrib.auth.models import AbstractUser
from django.db import models

from .validators import validate_username

LENGTH = 150
EMAIL_LENGTH = 254


class User(AbstractUser):
    email = models.EmailField(max_length=EMAIL_LENGTH, unique=True,
                              blank=False, null=False, verbose_name="Почта")

    username = models.CharField(validators=(validate_username,),
                                max_length=LENGTH, unique=True, blank=False,
                                null=False, verbose_name='Никнейм')

    first_name = models.CharField(max_length=LENGTH, blank=False,
                                  null=False, verbose_name="Имя")

    last_name = models.CharField(max_length=LENGTH, blank=False,
                                 null=False, verbose_name="Фамилия")

    USERNAME_FIELD = 'username'
    EMAIL_FIELD = ['email', ]

    def __str__(self):
        return self.username
