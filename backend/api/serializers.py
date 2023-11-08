import base64

from django.core.files.base import ContentFile
from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers

from recipes.models import Ingredient, Tag, Recipe, IngredientsInRecipe, \
    FavoriteRecipe, ListProducts
from rest_framework.exceptions import ValidationError
from rest_framework.fields import SerializerMethodField, IntegerField, \
    ImageField, ReadOnlyField
from rest_framework.relations import PrimaryKeyRelatedField
from rest_framework.validators import UniqueValidator

from users.models import User, Follow
from users.validators import validate_username


class CustomUserCreateSerializer(UserCreateSerializer):
    username = serializers.CharField(
        max_length=150, required=True,
        validators=[validate_username,
                    UniqueValidator(queryset=User.objects.all()), ])

    email = serializers.EmailField(max_length=254, required=True,
                                   validators=[UniqueValidator])

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'password')


class CustomUserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'is_subscribed')

    def get_is_subscribed(self, author):
        request = self.context.get('request')
        if request.user.is_anonymous:
            return False
        return Follow.objects.filter(user=request.user, author=author).exists()


class FollowSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'is_subscribed')


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
    amount = IntegerField()

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

    class Meta:
        model = Recipe
        fields = ('id', 'author', 'tags', 'ingredients', 'image', 'name',
                  'text', 'cooking_time', 'is_favorited',
                  'is_in_shopping_cart')

    def get_ingredients(self, recipe):
        ingredients = recipe.ingredientsinrecipe_set.values('ingredients__id',
                                                            'ingredients__name',
                                                            'ingredients__measurement_unit',
                                                            'amount')
        formatted_ingredients = []
        for ingredient in ingredients:
            formatted_ingredient = {'id': ingredient['ingredients__id'],
                                    'name': ingredient['ingredients__name'],
                                    'measurement_unit': ingredient[
                                        'ingredients__measurement_unit'],
                                    'amount': ingredient['amount']}
            formatted_ingredients.append(formatted_ingredient)

        return formatted_ingredients

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

        ingredients_list = []
        tags_list = []
        list_id_ingredients = Ingredient.objects.values_list('id', flat=True)
        for ingredient in ingredients:
            ingredient_id = ingredient.get('id')
            amount = ingredient.get('amount')
            if ingredient_id not in list_id_ingredients:
                raise ValidationError('Такого ингредиента нет!')
            if amount == 0:
                raise ValidationError('Кол-во ингредиента не может быть 0!')
            if ingredient in ingredients_list:
                raise ValidationError('Такой ингредиент уже есть!')
            ingredients_list.append(ingredient)

        for tag in tags:
            if tag in tags_list:
                raise ValidationError('Такой тэг уже есть!')
            tags_list.append(tag)
        return data

    def create(self, validated_data):
        tags_data = validated_data.pop('tags')
        ingredients_data = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags_data)
        IngredientsInRecipe.objects.bulk_create([IngredientsInRecipe(
            recipe=recipe, ingredients=Ingredient.objects.get(id=item['id']),
            amount=item['amount']) for item in ingredients_data])
        return recipe

    def update(self, instance, validated_data):
        tags_data = validated_data.pop('tags')
        ingredients_data = validated_data.pop('ingredients')
        instance = super().update(instance, validated_data)
        instance.tags.set(tags_data)
        IngredientsInRecipe.objects.filter(recipe=instance).delete()
        IngredientsInRecipe.objects.bulk_create([IngredientsInRecipe(
            recipe=instance, ingredients=Ingredient.objects.get(id=item['id']),
            amount=item['amount']) for item in ingredients_data])
        return instance

    def to_representation(self, instance):
        return RecipeSerializer(instance, context=self.context).data


class ShortRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор рецепта(укороченная версия)"""
    image = Base64ImageField(required=False, allow_null=True)

    class Meta:
        model = Recipe
        fields = ('id',
                  'name',
                  'image',
                  'cooking_time')
