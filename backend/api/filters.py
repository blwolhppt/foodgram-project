import django_filters
from django_filters.rest_framework import FilterSet, filters

from recipes.models import Recipe, Tag


class RecipeFilter(FilterSet):
    tags = django_filters.ModelMultipleChoiceFilter(field_name='tags__slug',
                                                    to_field_name='slug',
                                                    queryset=Tag.objects.all())

    is_favorited = filters.BooleanFilter(method='favorited')
    is_in_shopping_cart = filters.BooleanFilter(method='in_shopping_cart')

    class Meta:
        model = Recipe
        fields = ['author', 'tags', 'is_favorited', 'is_in_shopping_cart']

    def favorited(self, queryset, name, value):
        request = self.request
        if value:
            return queryset.filter(favoriterecipe__user_id=request.user.id)
        return queryset

    def in_shopping_cart(self, queryset, name, value):
        request = self.request
        if value:
            return queryset.filter(listproducts__user_id=request.user.id)
        return queryset
