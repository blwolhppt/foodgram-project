from rest_framework import serializers

from recipes.models import (Ingredient, Tag, Recipe, IngredientsInRecipe,
                            FavoriteRecipe)


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = '__all__'


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


class IngredientsInRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = IngredientsInRecipe
        fields = '__all__'


class RecipeSerializers(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = '__all__'

    def is_favorite(self, recipe):
        request = self.context.get('request')
        return request.user.is_authenticated and FavoriteRecipe.objects.filter(
            user=request.user, recipe=recipe).exists()


class FavoriteRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = FavoriteRecipe
        fields = '__all__'
