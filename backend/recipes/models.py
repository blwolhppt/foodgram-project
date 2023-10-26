from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

from users.models import User


class Ingredient(models.Model):
    name = models.CharField(max_length=200,
                            verbose_name='Название')
    measurement = models.CharField(max_length=10,
                                   verbose_name='Граммовки')

    class Meta:
        ordering = ['name']
        verbose_name = 'Ингредиенты'

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(max_length=200,
                            verbose_name='Название')

    color = models.CharField(max_length=10, verbose_name='Цвет')
    slug = models.SlugField(verbose_name='Cлаг')

    class Meta:
        ordering = ['id']
        verbose_name = 'Теги'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               verbose_name='Автор рецепта')

    tags = models.ManyToManyField(Tag,
                                  verbose_name='Тег')
    ingredients = models.ManyToManyField(Ingredient,
                                         verbose_name='Ингредиенты')
    image = models.ImageField(verbose_name='Картинка', upload_to='')
    name = models.CharField(max_length=200,
                            verbose_name='Название')
    text = models.CharField(max_length=200, verbose_name='Описание')
    cooking_time = models.IntegerField(default=10,
                                       validators=[MinValueValidator(1),
                                                   MaxValueValidator(100)],
                                       verbose_name='Время на рецепт')

    pub_date = models.DateTimeField(verbose_name='Дата', auto_now_add=True)

    class Meta:
        verbose_name = 'Рецепты'
        ordering = ['pub_date']

    def __str__(self):
        return self.name

