from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

from users.models import User

from .constants import (LENGTH, MIN_LENGTH, MIN_COOKING_TIME,
                        MAX_COOKING_TIME, DEFAULT_AMOUNT)


class Ingredient(models.Model):
    name = models.CharField(max_length=LENGTH,
                            verbose_name='Название')
    measurement_unit = models.CharField(max_length=MIN_LENGTH,
                                        verbose_name='Граммовки')

    class Meta:
        ordering = ['name']
        verbose_name = 'Ингредиенты'
        constraints = [
            models.UniqueConstraint(fields=['name', 'measurement_unit'],
                                    name='unique_name_measurement_unit')
        ]

    def __str__(self):
        return f'{self.name}, {self.measurement_unit}'


class Tag(models.Model):
    name = models.CharField(max_length=LENGTH,
                            verbose_name='Название', unique=True)

    color = models.CharField(max_length=7, verbose_name='Цвет', unique=True)
    slug = models.SlugField(max_length=LENGTH,
                            verbose_name='Cлаг', unique=True)

    class Meta:
        verbose_name = 'Теги'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               verbose_name='Автор рецепта')
    tags = models.ManyToManyField(Tag, verbose_name='Тег')
    ingredients = models.ManyToManyField(Ingredient,
                                         through='IngredientsInRecipe',
                                         verbose_name='Ингредиенты')
    image = models.ImageField(verbose_name='Картинка',
                              upload_to='recipes/')
    name = models.CharField(max_length=LENGTH,
                            verbose_name='Название')
    text = models.CharField(max_length=LENGTH, verbose_name='Описание')
    cooking_time = models.IntegerField(default=MIN_LENGTH,
                                       validators=[
                                           MinValueValidator(MIN_COOKING_TIME),
                                           MaxValueValidator(MAX_COOKING_TIME)
                                       ],
                                       verbose_name='Время на рецепт')

    pub_date = models.DateTimeField(verbose_name='Дата', auto_now_add=True)

    class Meta:
        verbose_name = 'Рецепты'
        ordering = ['-pub_date']

    def __str__(self):
        return self.name


class FavoriteRecipe(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             verbose_name='Автор рецепта')
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE,
                               verbose_name='Рецепт')

    class Meta:
        verbose_name = 'Любимые рецепты'

    def __str__(self):
        return f'{self.user}, {self.recipe}'


class IngredientsInRecipe(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE,
                               verbose_name='Рецепт')
    ingredients = models.ForeignKey(Ingredient, on_delete=models.CASCADE,
                                    verbose_name='Ингредиенты')
    amount = models.IntegerField(default=DEFAULT_AMOUNT,
                                 verbose_name='Количество')

    class Meta:
        verbose_name = 'Список ингредиентов для рецепта'

    def __str__(self):
        return f'{self.recipe}, {self.ingredients}, {self.amount}'


class ListProducts(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             verbose_name='Юзер')
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE,
                               verbose_name='Рецепт')

    class Meta:
        verbose_name = 'Список покупок'

    def __str__(self):
        return f'{self.user}, {self.recipe}'
