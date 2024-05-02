from celery import shared_task
from utils.otp import otp_sender as otp_sender_util
from celery import shared_task
from datetime import datetime, timedelta
from accounts.models import User


@shared_task
def otp_sender(email, username):
    otp_sender_util(email=email, username=username)


@shared_task
def delete_old_records():
    time_delta = datetime.now() - timedelta(hours=72)

    User.global_objects.filter(created_at__lte=time_delta, is_active=False).delete()
