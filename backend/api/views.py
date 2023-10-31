from rest_framework import viewsets
from rest_framework.pagination import LimitOffsetPagination


from api import serializers

from recipes.models import Recipe, Tag, Ingredient


# Create your views here.
class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = serializers.RecipeSerializers
    pagination_class = LimitOffsetPagination


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = serializers.IngredientSerializer


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = serializers.TagSerializer


class UsersViewSet(viewsets.ModelViewSet):
    pass


