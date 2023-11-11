from djoser.serializers import UserCreateSerializer, UserSerializer

from rest_framework import serializers

from rest_framework.validators import UniqueValidator

from .models import User, Follow
from .validators import validate_username

from .constants import LENGTH, EMAIL_LENGTH


class CustomUserCreateSerializer(UserCreateSerializer):
    username = serializers.CharField(
        max_length=LENGTH, required=True,
        validators=[validate_username,
                    UniqueValidator(queryset=User.objects.all())])

    email = serializers.EmailField(max_length=EMAIL_LENGTH, required=True,
                                   validators=[UniqueValidator])

    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'first_name',
                  'last_name', 'password')


class CustomUserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'first_name',
                  'last_name', 'is_subscribed')

    def get_is_subscribed(self, author):
        request = self.context.get('request')
        if request.user and request.user.is_authenticated:
            return Follow.objects.filter(user=request.user,
                                         author=author).exists()
        return False
