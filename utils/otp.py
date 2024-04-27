from accounts.models import User
import random
from django.core.mail import send_mail
from django.core.cache import cache


def otp_sender(user: User):
    otp = random.randint(100000, 999999)
    otp_if_not_expired = cache.get(f"{user.email}")
    if not otp_if_not_expired:
        cache.set(f"{user.email}", otp, timeout=300)
        subject = 'OTP Verification'
        message = f'Welcome to Our Online Shop\nDear {user.username},\n\nYour OTP is {otp}'
        from_email = 'balaghi.hamid.django@gmail.com'
        to_email = user.email
        send_mail(subject, message, from_email, [to_email])
