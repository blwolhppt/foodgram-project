import django_filters
from recipes.models import Recipe, Tag


class RecipeFilter(django_filters.FilterSet):
    tags = django_filters.ModelMultipleChoiceFilter(field_name='tags__slug',
                                                    to_field_name='slug',
                                                    queryset=Tag.objects.all())
    is_favorited = django_filters.BooleanFilter(method='get_is_favorited')

    class Meta:
        model = Recipe
        fields = ['author', 'tags']
