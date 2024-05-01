import random
from django.core.mail import send_mail
from django.core.cache import cache


def otp_sender(email, username):
    otp = random.randint(100000, 999999)
    otp_if_not_expired = cache.get(f"{email}")
    if not otp_if_not_expired:
        cache.set(f"{email}", otp, timeout=300)
        subject = 'OTP Verification'
        message = f'Welcome to Our Online Shop\nDear {username},\n\nYour OTP is {otp}'
        from_email = 'balaghi.hamid.django@gmail.com'
        to_email = email
        send_mail(subject, message, from_email, [to_email])
