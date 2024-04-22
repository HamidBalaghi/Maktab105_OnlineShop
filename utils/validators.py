from django.core.exceptions import ValidationError
from django.utils import timezone


def validate_not_in_past(value):
    if value < timezone.now().date():
        raise ValidationError('Date cannot be in the past.')


# def validate_paid_time_unchanged(instance):
#     if instance.pk is not None:
#         original_instance = instance.__class__.objects.get(pk=instance.pk)
#         if original_instance.paid_time is not None and original_instance.paid_time != instance.paid_time:
#             raise ValidationError("Once paid_time is set, it cannot be changed.")
