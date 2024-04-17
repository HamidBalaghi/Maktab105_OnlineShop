from django.core.exceptions import ValidationError
from django.utils import timezone


def validate_not_in_past(value):
    if value < timezone.now().date():
        raise ValidationError('Date cannot be in the past.')
