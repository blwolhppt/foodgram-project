from django.urls import path, include
from rest_framework.routers import SimpleRouter
from api import views

router = SimpleRouter()

router.register('recipes', views.RecipeViewSet)
router.register('ingredients', views.IngredientViewSet)
router.register('tags', views.TagViewSet)
router.register('users', views.CustomUserViewSet)


urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('djoser.urls.authtoken'))
]
