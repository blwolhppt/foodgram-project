from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination

from api import serializers

from recipes.models import Recipe, Tag, Ingredient, FavoriteRecipe, \
    ListProducts, IngredientsInRecipe
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api import permissions
from users.models import User, Follow


class CustomUserViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = serializers.CustomUserSerializer
    pagination_class = LimitOffsetPagination
    http_method_names = ['get', 'post', 'delete', 'patch']

    def get_permissions(self):
        if self.action == 'list':
            return [permissions.AllowAny()]
        return super().get_permissions()

    @action(
        detail=True,
        methods=('POST', 'DELETE',),
        permission_classes=(IsAuthenticated,)
    )
    def change_favorite(self, request):
        if request.method == 'POST':
            return self.add_subscribe(request)
        if request.method == 'DELETE':
            return self.delete_subscribe(request)

    def add_subscribe(self, request):
        author = get_object_or_404(User, id=self.kwargs.get("id"))
        serializer = serializers.FollowSerializer(
            author, data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        Follow.objects.create(user=request.user, author=author)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete_subscribe(self, request):
        Follow.objects.get(user=request.user,
                           author=get_object_or_404(User,
                                                    id=self.kwargs.get(
                                                        "id"))).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=('GET',),
        permission_classes=(IsAuthenticated,))
    def me(self, request):
        serializer = serializers.CustomUserSerializer(
            request.user, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = serializers.IngredientSerializer
    pagination_class = None

    filter_backends = [filters.SearchFilter]
    search_fields = ['name']

    def get_queryset(self):
        queryset = super().get_queryset()
        ingredient_name = self.request.query_params.get('name', None)

        if ingredient_name:
            queryset = queryset.filter(name__startswith=ingredient_name)
        return queryset


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = serializers.TagSerializer
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    pagination_class = LimitOffsetPagination
    permission_classes = (permissions.OwnerOrReadOnly,)
    http_method_names = ['get', 'post', 'delete', 'patch']

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return serializers.RecipeSerializer
        return serializers.NewRecipeSerializer

    @action(
        detail=True,
        methods=('POST', 'DELETE',),
        permission_classes=(IsAuthenticated,)
    )
    def change_favorite(self, request):
        if request.method == 'POST':
            return self.favorite(FavoriteRecipe, request)
        if request.method == 'DELETE':
            return self.delete_favorite(FavoriteRecipe, request)

    def favorite(self, request, pk):
        recipe = get_object_or_404(Recipe, id=pk)
        favorite_create = FavoriteRecipe.objects.create(
            user=request.user, recipe=recipe)
        serializer = serializers.FavoriteRecipeSerializer(
            favorite_create, context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete_favorite(self, request, pk):
        recipe = get_object_or_404(Recipe, id=pk)
        favorite_recipe = get_object_or_404(FavoriteRecipe, user=request.user,
                                            recipe=recipe)
        favorite_recipe.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=('POST', 'DELETE',),
        permission_classes=(IsAuthenticated,)
    )
    def shopping_cart(self, request, pk):
        recipe = get_object_or_404(Recipe, id=pk)
        if request.method == 'POST':
            return self.add_to_shopping_cart(request, recipe)
        elif request.method == 'DELETE':
            return self.delete_from_shopping_cart(request, recipe)

    def add_to_shopping_cart(self, request, recipe):
        if ListProducts.objects.filter(user=request.user,
                                       recipe=recipe).exists():
            return Response({'errors': 'Рецепт уже добавлен!'},
                            status=status.HTTP_400_BAD_REQUEST)
        ListProducts.objects.create(user=request.user, recipe=recipe)
        serializer = serializers.RecipeSerializer(recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete_from_shopping_cart(self, request, recipe):
        recipe_entry = ListProducts.objects.filter(user=request.user,
                                                   recipe=recipe)
        if recipe_entry.exists():
            recipe_entry.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response({'errors': 'Рецепт уже удален!'},
                        status=status.HTTP_400_BAD_REQUEST)
