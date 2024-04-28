from django.db import models
from django.core.validators import RegexValidator
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from .managers import UserManager
from core.models import LogicalMixin, TimeStampMixin


class User(LogicalMixin, AbstractBaseUser, PermissionsMixin, TimeStampMixin):
    email = models.CharField(max_length=100, unique=True, validators=[
        RegexValidator(
            regex='^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
            message='Enter a valid email address'
        )
    ])
    username = models.CharField(max_length=255, unique=True)  ##todo:make a validator for username
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.username
