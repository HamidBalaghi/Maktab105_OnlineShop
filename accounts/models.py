from django.db import models
from django.core.validators import RegexValidator
from django.contrib.auth.models import AbstractBaseUser
from .managers import UserManager
from core.models import LogicalMixin, TimeStampMixin


class User(LogicalMixin, AbstractBaseUser, TimeStampMixin):
    email = models.CharField(max_length=100, unique=True, validators=[
        RegexValidator(
            regex='^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
            message='Enter a valid email address'
        )
    ])

    username = models.CharField(max_length=255, unique=True)  ##todo:make a validator for username
    is_active = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', ]

    def __str__(self):
        return f"{self.username}"

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    @property
    def is_staff(self):
        return self.is_admin
