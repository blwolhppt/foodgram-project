import re

from django.core.exceptions import ValidationError


def validate_username(username):
    forbidden_symb = re.sub(r"^[\w.@+-]+\Z", ' ', username)
    if username == 'me':
        raise ValidationError('Недопустимое имя пользователя!')
    elif username in forbidden_symb:
        raise ValidationError('Не допустимые символы в имени пользователя')
    return username
