import re
from django.core.exceptions import ValidationError
from django.utils import timezone
from rest_framework import serializers


def validate_year(value):
    if value > timezone.now().year:
        raise ValidationError(
            'Год %(value)s больше текущего!',
            params={'value': value},
        )


def username_validate(value):
    user_regex = re.compile(r"^[\w-]+$")
    if not user_regex.match(value):
        raise serializers.ValidationError(
            'Вы использовали запрещенные символы!'
        )
    if value.lower() == 'me':
        raise serializers.ValidationError(
            "Имя пользователя не может быть 'me'."
        )
    return value
