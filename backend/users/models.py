from django.contrib.auth.models import AbstractUser
from django.db import models

from .validators import validate_username

LENGTH = 150
EMAIL_LENGTH = 254


class User(AbstractUser):
    email = models.EmailField(max_length=EMAIL_LENGTH,
                              unique=True,
                              blank=False,
                              null=False,
                              verbose_name="Почта")

    username = models.CharField(validators=(validate_username,),
                                max_length=LENGTH,
                                unique=True,
                                blank=False,
                                null=False,
                                verbose_name='Никнейм')

    first_name = models.CharField(max_length=LENGTH,
                                  blank=False,
                                  null=False,
                                  verbose_name="Имя")

    last_name = models.CharField(max_length=LENGTH,
                                 blank=False,
                                 null=False,
                                 verbose_name="Фамилия")

    password = models.CharField(max_length=LENGTH,
                                verbose_name="Пароль")

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('username', 'first_name', 'last_name')

    def __str__(self):
        return self.username


class Follow(models.Model):
    user = models.ForeignKey(User,
                             default=None,
                             on_delete=models.CASCADE,
                             related_name="follower",
                             verbose_name="Подписчик")
    author = models.ForeignKey(User,
                               default=None,
                               on_delete=models.CASCADE,
                               related_name="followed",
                               verbose_name="Автор")

    def __str__(self):
        return f'{self.user}, {self.author}'
