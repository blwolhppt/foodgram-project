from django.urls import path, include
from rest_framework.routers import SimpleRouter
from api import views

router = SimpleRouter()

router.register('recipe', views.RecipeViewSet)
router.register('ingredient', views.IngredientViewSet)
router.register('tag', views.TagViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
