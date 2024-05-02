from django.db import models
from django.core.validators import RegexValidator
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from .managers import UserManager
from core.models import LogicalMixin, TimeStampMixin
from django.utils.translation import gettext_lazy as _


class User(LogicalMixin, AbstractBaseUser, PermissionsMixin, TimeStampMixin):
    email = models.CharField(verbose_name=_("Email"), max_length=100, unique=True, validators=[
        RegexValidator(
            regex='^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
            message='Enter a valid email address'
        )
    ])
    username = models.CharField(verbose_name=_("Username"), max_length=255,
                                unique=True)  ##todo:make a validator for username
    is_active = models.BooleanField(verbose_name=_("Is_active"), default=False)
    is_staff = models.BooleanField(verbose_name=_("Is_staff"), default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.username

    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')
