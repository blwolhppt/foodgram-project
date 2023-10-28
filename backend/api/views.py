from django.shortcuts import render
from rest_framework import viewsets


# Create your views here.
class RecipeViewSet(viewsets.ModelViewSet):
    pass


class IngredientViewSet(viewsets.ModelViewSet):
    pass


class TagViewSet(viewsets.ModelViewSet):
    pass


class UsersViewSet(viewsets.ModelViewSet):
    pass
