from accounts.models import User
import random
from django.core.mail import send_mail
from accounts.models import OTPModel
from django.utils import timezone
from datetime import timedelta


def is_otp_expired(otp_model: OTPModel):
    limit_time = timezone.now() - timedelta(minutes=5)
    return otp_model.updated_at < limit_time


def otp_sender(user: User):
    otp = random.randint(100000, 999999)
    otp_model, created = OTPModel.objects.get_or_create(user=user)
    if created or (not created and is_otp_expired(otp_model)):
        otp_model.code = otp
        otp_model.save()
        subject = 'OTP Verification'
        message = f'Welcome to Our Online Shop\nDear {user.username},\n\nYour OTP is {otp}'
        from_email = 'balaghi.hamid.django@gmail.com'
        to_email = user.email
        send_mail(subject, message, from_email, [to_email])
