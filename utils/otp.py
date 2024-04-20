from accounts.models import User
import random
from django.core.mail import send_mail
from accounts.models import OTPModel


def otp_sender(user: User):
    otp = random.randint(100000, 999999)
    OTPModel.objects.create(user=user, code=otp)
    subject = 'OTP Verification'
    message = f'Welcome to Our Online Shop\nDear {user.username},\n\nYour OTP is {otp}'
    from_email = 'balaghi.hamid.django@gmail.com'
    to_email = user.email
    send_mail(subject, message, from_email, [to_email])
