from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.pagination import LimitOffsetPagination

from api import serializers

from recipes.models import Recipe, Tag, Ingredient, FavoriteRecipe
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.permissions import OwnerOrReadOnly, AllowAny
from rest_framework.views import APIView

from users.models import User, Follow


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = serializers.RecipeSerializers
    permission_classes = (OwnerOrReadOnly,)
    pagination_class = LimitOffsetPagination
    http_method_names = ['get', 'post', 'delete', 'patch']

    def favorite(self, request, id):
        recipe = get_object_or_404(Recipe, id=id)
        favorite_create = FavoriteRecipe.objects.create(
            user=request.user, recipe=recipe)
        serializer = serializers.FavoriteRecipeSerializer(
            favorite_create, context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete_favorite(self, request, id):
        recipe = get_object_or_404(Recipe, id=id)
        if get_object_or_404(FavoriteRecipe, user=request.user,
                             recipe=recipe).delete():
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=('POST', 'DELETE',)
    )
    def change_favorite(self, request):
        if request.method == 'POST':
            return self.favorite(FavoriteRecipe, request)
        if request.method == 'DELETE':
            return self.delete_favorite(FavoriteRecipe, request)


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


class CustomUserViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = serializers.CustomUserSerializer
    permission_classes = (AllowAny,)
    pagination_class = LimitOffsetPagination
    http_method_names = ['get', 'post', 'delete', 'patch']

    @action(detail=False,
            methods=('POST',),
            permission_classes=(IsAuthenticated,))
    def add_subscribe(self, request):
        author = get_object_or_404(User, id=self.kwargs.get("id"))
        serializer = serializers.FollowSerializer(
            author, data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        Follow.objects.create(user=request.user, author=author)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False,
            methods=('POST',),
            permission_classes=(IsAuthenticated,))
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
        user = request.user
        serializer = serializers.CustomUserSerializer(
            user, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)
