from django.contrib.auth.models import AbstractUser
from django.db import models

from .constants import EMAIL_LENGTH, LENGTH
from .validators import validate_username


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

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'author'],
                                    name='unique_user_author')
        ]

    def __str__(self):
        return f'{self.user}, {self.author}'
