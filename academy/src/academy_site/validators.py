from django.utils import timezone

from django.core.exceptions import ValidationError


def positive_number(value):
    if value <= 0:
        raise ValidationError('This field must be an positive number.')
