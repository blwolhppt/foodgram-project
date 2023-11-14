from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from reportlab.pdfgen import canvas

from api import permissions, serializers
from api.filters import RecipeFilter
from recipes.models import (Recipe, Tag, Ingredient, FavoriteRecipe,
                            ListProducts)


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
    filter_backends = [DjangoFilterBackend]
    filterset_class = RecipeFilter

    http_method_names = ['get', 'post', 'delete', 'patch']

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return serializers.RecipeSerializer
        return serializers.NewRecipeSerializer

    @action(detail=True,
            methods=('POST',),
            permission_classes=[IsAuthenticated])
    def favorite(self, request, pk):
        return self.add_favorite(request, pk)

    @favorite.mapping.delete
    def delete_favorite(self, request, pk):
        recipe = get_object_or_404(Recipe, id=pk)
        get_object_or_404(FavoriteRecipe, user=request.user,
                          recipe=recipe).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def add_favorite(self, request, pk):
        recipe = get_object_or_404(Recipe, id=pk)
        recipe_instance = FavoriteRecipe(user=request.user, recipe=recipe)
        serializer = serializers.FavoriteRecipeSerializer(
            instance=recipe_instance,
            data=request.data,
            context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(
        detail=True,
        methods=('POST',),
        permission_classes=(IsAuthenticated,)
    )
    def shopping_cart(self, request, pk):
        return self.add_shopping_cart(request, pk)

    def add_shopping_cart(self, request, pk):
        recipe = get_object_or_404(Recipe, id=pk)
        recipe_instance = ListProducts(user=request.user, recipe=recipe)
        serializer = serializers.ListProductsSerializer(
            instance=recipe_instance,
            data=request.data,
            context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @shopping_cart.mapping.delete
    def delete_shopping_cart(self, request, pk):
        recipe = get_object_or_404(Recipe, id=pk)
        get_object_or_404(ListProducts, user=request.user,
                          recipe=recipe).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=('GET',),
        permission_classes=(IsAuthenticated,),
    )
    def download_shopping_cart(self, request):
        ingredients = (Recipe.objects.filter(
            listproducts__user=request.user).values(
            'ingredients__name', 'ingredients__measurement_unit')
            .order_by("ingredient__name"))

        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = ('attachment; filename="'
                                           'shopping_cart.pdf"')

        pdf = canvas.Canvas(response)

        pdf.drawString('Что купить:')

        y_position = 780

        for ing in ingredients:
            ingredient_text = (f'{ing["ingredients__name"]} '
                               f'({ing["ingredients__measurement_unit"]})')
            pdf.drawString(100, y_position, ingredient_text.encode(
                'utf-8').decode('latin-1'))
            y_position -= 20

        pdf.showPage()
        pdf.save()

        return response
