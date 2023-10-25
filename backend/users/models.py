from django.contrib.auth.models import AbstractUser
from django.db import models

LENGTH = 150


class User(AbstractUser):
    email = models.EmailField(max_length=254, unique=True, blank=False,
                              null=False, verbose_name="Почта")

    username = models.CharField(max_length=LENGTH, unique=True, blank=False,
                                null=False, verbose_name='Никнейм')

    first_name = models.CharField(max_length=LENGTH, blank=False,
                                  null=False, verbose_name="Имя")

    last_name = models.CharField(max_length=LENGTH, blank=False,
                                 null=False, verbose_name="Фамилия")

    REQUIRED_FIELDS = ['email', 'username', 'first_name', 'last_name']

    def __str__(self):
        return self.username
