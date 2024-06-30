from celery import shared_task
from datetime import datetime
from .models import Discount


@shared_task
def delete_expired_discounts():

    expired = Discount.objects.filter(expiration_date__lt=datetime.now().date(), is_deleted=False)
    for discount in expired:
        discount.is_deleted = True
        discount.save()