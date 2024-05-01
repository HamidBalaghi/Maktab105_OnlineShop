from celery import shared_task
from utils.otp import otp_sender as otp_sender_util


@shared_task
def otp_sender(email, username):
    otp_sender_util(email=email, username=username)
