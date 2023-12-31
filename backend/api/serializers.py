import base64

from django.core.files.base import ContentFile
from django.core.validators import MinValueValidator, MaxValueValidator
from djoser.serializers import UserSerializer
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.fields import (SerializerMethodField, IntegerField,
                                   ImageField, ReadOnlyField)
from rest_framework.relations import PrimaryKeyRelatedField

from recipes.models import (Ingredient, Tag, Recipe, IngredientsInRecipe,
                            FavoriteRecipe, ListProducts)
from recipes.constants import (MAX_COOKING_TIME, MIN_AMMOUNT_INGREDIENTS,
                               MIN_COOKING_TIME)
from users.models import Follow
from users.serializers import CustomUserSerializer


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = '__all__'


class IngredientsInRecipeSerializer(serializers.ModelSerializer):
    id = IntegerField(write_only=True)
    amount = IntegerField(validators=[MinValueValidator(1),
                                      MaxValueValidator(500)])

    class Meta:
        model = IngredientsInRecipe
        fields = ('id', 'amount')


class Base64ImageField(ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)


class RecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True)
    author = CustomUserSerializer()
    ingredients = SerializerMethodField()
    image = Base64ImageField()
    is_favorited = SerializerMethodField()
    is_in_shopping_cart = SerializerMethodField()
    cooking_time = serializers.IntegerField(
        validators=[MinValueValidator(MIN_COOKING_TIME),
                    MaxValueValidator(MAX_COOKING_TIME)])

    class Meta:
        model = Recipe
        fields = ('id', 'author', 'tags', 'ingredients', 'image', 'name',
                  'text', 'cooking_time', 'is_favorited',
                  'is_in_shopping_cart')

    def get_ingredients(self, recipe):
        ingredients = recipe.ingredientsinrecipe_set.values(
            'ingredients__id',
            'ingredients__name',
            'ingredients__measurement_unit',
            'amount')
        form_ingredients = []
        for ingredient in ingredients:
            formatted_ingredient = {'id': ingredient['ingredients__id'],
                                    'name': ingredient['ingredients__name'],
                                    'measurement_unit': ingredient[
                                        'ingredients__measurement_unit'],
                                    'amount': ingredient['amount']}
            form_ingredients.append(formatted_ingredient)

        return form_ingredients

    def get_is_favorited(self, recipe):
        request = self.context.get('request')
        return request.user.is_authenticated and FavoriteRecipe.objects.filter(
            user=request.user, recipe=recipe).exists()

    def get_is_in_shopping_cart(self, recipe):
        request = self.context.get('request')
        return request.user.is_authenticated and ListProducts.objects.filter(
            user=request.user, recipe=recipe).exists()


class NewRecipeSerializer(serializers.ModelSerializer):
    tags = PrimaryKeyRelatedField(queryset=Tag.objects.all(), many=True)
    author = CustomUserSerializer(read_only=True)
    ingredients = IngredientsInRecipeSerializer(many=True)
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'author', 'tags', 'ingredients', 'image', 'name',
                  'text', 'cooking_time')

    def validate(self, data):
        ingredients = data.get('ingredients')
        cooking_time = data.get('cooking_time')
        tags = data.get('tags')
        if not cooking_time or not ingredients or not tags:
            raise ValidationError('Надо указать обязательные поля!')

        list_ingredients = []
        list_tags = []
        list_id_ingredients = Ingredient.objects.values_list('id', flat=True)
        for ingredient in ingredients:
            ingredient_id = ingredient.get('id')
            amount = ingredient.get('amount')
            if ingredient_id not in list_id_ingredients:
                raise ValidationError('Такого ингредиента нет!')
            if amount < MIN_AMMOUNT_INGREDIENTS:
                raise ValidationError(f'Кол-во ингредиента не может быть '
                                      f'меньше {MIN_AMMOUNT_INGREDIENTS}!')
            if ingredient in list_ingredients:
                raise ValidationError('Такой ингредиент уже есть!')
            list_ingredients.append(ingredient)

        for tag in tags:
            if tag in list_tags:
                raise ValidationError('Такой тэг уже есть!')
            list_tags.append(tag)
        return data

    def create(self, validated_data):
        tags_data = validated_data.get('tags')
        ingredients_data = validated_data.get('ingredients')
        validated_data.pop('tags', None)
        validated_data.pop('ingredients', None)
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags_data)
        ingredients_in_recipe = []
        for item in ingredients_data:
            ingredient = Ingredient.objects.get(id=item['id'])
            amount = item['amount']
            ingredients_in_recipe.append(
                IngredientsInRecipe(recipe=recipe, ingredients=ingredient,
                                    amount=amount))
        IngredientsInRecipe.objects.bulk_create(ingredients_in_recipe)
        return recipe

    def update(self, recipe, validated_data):
        tags_data = validated_data.get('tags')
        ingredients_data = validated_data.get('ingredients')
        validated_data.pop('tags', None)
        validated_data.pop('ingredients', None)
        IngredientsInRecipe.objects.filter(recipe=recipe).delete()

        recipe = super().update(recipe, validated_data)
        recipe.tags.set(tags_data)

        for item in ingredients_data:
            ingredient = Ingredient.objects.get(id=item['id'])
            amount = item['amount']
            IngredientsInRecipe.objects.create(
                recipe=recipe, ingredients=ingredient, amount=amount)
        return recipe

    def to_representation(self, instance):
        return RecipeSerializer(instance, context=self.context).data


class RecipeFollowSerializer(serializers.ModelSerializer):
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class FollowSerializer(UserSerializer):
    is_subscribed = SerializerMethodField()
    recipes = SerializerMethodField()
    recipes_count = SerializerMethodField()

    class Meta:
        model = Follow
        fields = ('id', 'user', 'author',
                  'is_subscribed', 'recipes', 'recipes_count')

    def validate(self, data):
        instance = self.instance
        user = instance.user
        author = instance.author
        if Follow.objects.filter(author=author, user=user).exists():
            raise ValidationError('Уже есть такая подписка')
        if user == author:
            raise ValidationError('Нельзя подписаться на самого себя!')
        return data

    def get_is_subscribed(self, request):
        return Follow.objects.filter(user=request.user,
                                     author=request.author).exists()

    def get_recipes(self, data):
        request = self.context.get('request')
        limit = request.GET.get('recipes_limit')
        queryset = (Recipe.objects.filter(author=data.author)[:int(limit)]
                    if limit else Recipe.objects.filter(author=data.author))
        recipes = RecipeFollowSerializer(queryset, many=True).data
        return recipes

    def get_recipes_count(self, data):
        request = self.context.get('request')
        limit = request.GET.get('recipes_limit')
        queryset = (Recipe.objects.filter(author=data.author)[:int(limit)]
                    if limit else Recipe.objects.filter(author=data.author))
        return len(queryset)

    def to_representation(self, instance):
        representation = {
            'id': instance.author.id,
            'email': instance.author.email,
            'username': instance.author.username,
            'first_name': instance.author.first_name,
            'last_name': instance.author.last_name,
            'is_subscribed': self.get_is_subscribed(instance),
            'recipes': self.get_recipes(instance),
            'recipes_count': self.get_recipes_count(instance),
        }
        return representation


class FavoriteRecipeSerializer(serializers.ModelSerializer):
    name = ReadOnlyField(source='recipe.name')
    image = Base64ImageField(source='recipe.image', read_only=True)
    cooking_time = ReadOnlyField(source='recipe.cooking_time')

    class Meta:
        model = FavoriteRecipe
        fields = ('id', 'name', 'image', 'cooking_time')

    def validate(self, data):
        instance = self.instance
        recipe = instance.recipe.id
        user = instance.user
        if FavoriteRecipe.objects.filter(user=user, recipe_id=recipe).exists():
            raise ValidationError('Рецепт уже есть в избранном')
        return data


class ListProductsSerializer(serializers.ModelSerializer):
    name = ReadOnlyField(source='recipe.name')
    image = Base64ImageField(source='recipe.image', read_only=True)
    cooking_time = ReadOnlyField(source='recipe.cooking_time')

    class Meta:
        model = FavoriteRecipe
        fields = ('id', 'name', 'image', 'cooking_time')

    def validate(self, data):
        instance = self.instance
        recipe = instance.recipe.id
        user = instance.user
        if ListProducts.objects.filter(user=user, recipe_id=recipe).exists():
            raise ValidationError('Рецепт уже есть в корзине')
        return data
