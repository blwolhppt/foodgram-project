from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from reportlab.pdfgen import canvas

from api import permissions
from api import serializers
from api.filters import RecipeFilter
from recipes.models import (Recipe, Tag, Ingredient, FavoriteRecipe,
                            ListProducts)
from users.models import User, Follow


class CustomUserViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = serializers.CustomUserSerializer
    pagination_class = LimitOffsetPagination

    http_method_names = ['get', 'post', 'delete', 'patch']

    def get_permissions(self):
        if self.action == 'list':
            return [AllowAny()]
        return super().get_permissions()

    @action(
        detail=True,
        methods=('POST', 'DELETE',),
        permission_classes=(IsAuthenticated,)
    )
    def subscribe(self, request, **kwargs):
        user = request.user
        author = get_object_or_404(User, id=kwargs.get('id'))
        if request.method == 'POST':
            return self.subscribe_to_author(user, author)
        if request.method == 'DELETE':
            return self.unsubscribe_to_author(user, author)

    def subscribe_to_author(self, user, author):
        if user == author or Follow.objects.filter(
                user=user, author=author).exists():
            return Response(status=status.HTTP_400_BAD_REQUEST)

        serializer = serializers.FollowSerializer(Follow.objects.create(
            user=user, author=author), context={'request': self.request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def unsubscribe_to_author(self, user, author):
        if Follow.objects.filter(user=user, author=author).exists():
            Follow.objects.filter(user=user, author=author).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(
        detail=False,
        permission_classes=(IsAuthenticated,)
    )
    def subscriptions(self, request):
        subs = self.paginate_queryset(Follow.objects.filter(user=request.user))
        serializer = serializers.FollowSerializer(subs, many=True,
                                                  context={'request': request})
        return self.get_paginated_response(serializer.data)

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
    permission_classes = (permissions.IsAuthenticatedAuthorOrReadOnly,)
    filter_backends = [SearchFilter, DjangoFilterBackend]
    filterset_class = RecipeFilter
    search_fields = ['name', 'ingredients__name', 'tags__name']

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
    def favorite(self, request, **kwargs):
        if request.method == 'POST':
            return self.add_favorite(request, kwargs.get('pk'))
        if request.method == 'DELETE':
            return self.delete_favorite(request, kwargs.get('pk'))

    def add_favorite(self, request, pk):
        try:
            recipe = Recipe.objects.get(id=pk)
        except Recipe.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        if FavoriteRecipe.objects.filter(user=request.user,
                                         recipe=recipe).exists():
            return Response(status=status.HTTP_400_BAD_REQUEST)
        serializer = serializers.FavoriteRecipeSerializer(
            FavoriteRecipe.objects.create(user=request.user, recipe=recipe),
            context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete_favorite(self, request, pk):
        recipe = get_object_or_404(Recipe, id=pk)
        if get_object_or_404(FavoriteRecipe, user=request.user,
                             recipe=recipe).delete():
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(
        detail=True,
        methods=('POST', 'DELETE',),
        permission_classes=(IsAuthenticated,)
    )
    def shopping_cart(self, request, **kwargs):
        if request.method == 'POST':
            return self.add_shopping_cart(request, kwargs.get('pk'))
        if request.method == 'DELETE':
            return self.delete_shopping_cart(request, kwargs.get('pk'))

    def add_shopping_cart(self, request, pk):
        try:
            recipe = Recipe.objects.get(id=pk)
        except Recipe.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        if ListProducts.objects.filter(user=request.user,
                                       recipe=recipe).exists():
            return Response(status=status.HTTP_400_BAD_REQUEST)
        serializer = serializers.FavoriteRecipeSerializer(
            ListProducts.objects.create(user=request.user, recipe=recipe),
            context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete_shopping_cart(self, request, pk):
        recipe = get_object_or_404(Recipe, id=pk)
        if get_object_or_404(ListProducts, user=request.user,
                             recipe=recipe).delete():
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(
        detail=False,
        methods=('GET',),
        permission_classes=(IsAuthenticated, ),
    )
    def download_shopping_cart(self, request):
        ingredients = Recipe.objects.filter(
            listproducts__user=request.user).values(
            'ingredients__name', 'ingredients__measurement_unit')

        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = \
            'attachment; filename="shopping_cart.pdf"'

        pdf = canvas.Canvas(response)

        pdf.drawString('Что купить:')

        y_position = 780

        for ing in ingredients:
            ingredient_text = f'{ing["ingredients__name"]} ' \
                              f'({ing["ingredients__measurement_unit" ]})'
            pdf.drawString(100, y_position, ingredient_text.encode(
                'utf-8').decode('latin-1'))
            y_position -= 20

        pdf.showPage()
        pdf.save()

        return response
