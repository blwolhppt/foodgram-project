from django.contrib import admin

from .models import Ingredient, Tag, Recipe, FavoriteRecipe, \
    IngredientsInRecipe, ListProducts

admin.site.register(Ingredient)
admin.site.register(Tag)
admin.site.register(Recipe)
admin.site.register(FavoriteRecipe)
admin.site.register(IngredientsInRecipe)
admin.site.register(ListProducts)

