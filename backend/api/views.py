from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination

from api import serializers

from recipes.models import Recipe, Tag, Ingredient, FavoriteRecipe
from rest_framework.response import Response


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = serializers.RecipeSerializers
    pagination_class = LimitOffsetPagination
    http_method_names = ['get', 'post', 'delete', 'patch']

    def favorite(self, request, pk):
        recipe = get_object_or_404(Recipe, id=pk)
        favorite_create = FavoriteRecipe.objects.create(
            user=request.user, recipe=recipe)
        serializer = serializers.FavoriteRecipeSerializer(
            favorite_create, context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete_favorite(self, request, pk):
        recipe = get_object_or_404(Recipe, id=pk)
        if get_object_or_404(FavoriteRecipe, user=request.user,
                             recipe=recipe).delete():
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=('POST', 'DELETE')
    )
    def change_favorite(self, request):
        if request.method == 'POST':
            return self.favorite(FavoriteRecipe, request)
        if request.method == 'DELETE':
            return self.delete_favorite(FavoriteRecipe, request)


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = serializers.IngredientSerializer
    pagination_class = None


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = serializers.TagSerializer
    pagination_class = None
