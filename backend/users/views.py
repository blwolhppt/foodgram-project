from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .models import User, Follow
from .serializers import CustomUserSerializer

from api import serializers


class CustomUserViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    pagination_class = LimitOffsetPagination

    http_method_names = ['get', 'post', 'delete', 'patch']

    def get_permissions(self):
        if self.action == 'list':
            return [AllowAny()]
        return super().get_permissions()

    @action(
        detail=True,
        methods=('POST',),
        permission_classes=(IsAuthenticated,)
    )
    def subscribe(self, request, **kwargs):
        user = request.user
        author = get_object_or_404(User, id=kwargs.get('id'))
        if user == author or Follow.objects.filter(user=user,
                                                   author=author).exists():
            return Response(status=status.HTTP_400_BAD_REQUEST)
        serializer = serializers.FollowSerializer(Follow.objects.create(
            user=user, author=author), context={'request': self.request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @subscribe.mapping.delete
    def unsubscribe(self, request, **kwargs):
        user = request.user
        author = get_object_or_404(User, id=kwargs.get('id'))
        get_object_or_404(Follow.objects.filter(user=user,
                                                author=author)).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


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
