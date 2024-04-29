from django.core.validators import RegexValidator
from django.db import models
from django.db.models import UniqueConstraint, Q
from accounts.models import User
from core.models import TimeStampMixin, LogicalMixin
from django.utils.translation import gettext_lazy as _


class Customer(LogicalMixin, TimeStampMixin):
    customer = models.ForeignKey(User, verbose_name=_("Customer"), on_delete=models.SET_NULL, null=True,
                                 related_name='customers')
    phone_number = models.CharField(verbose_name=_("Phone number"), max_length=11, unique=True, null=True, blank=True)
    customer_type = models.SmallIntegerField(verbose_name=_("Customer type"), default=5)

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=['customer'],
                condition=Q(is_deleted=False),
                name='unique_not_deleted_customer'
            )
        ]
        verbose_name = _("Customer")
        verbose_name_plural = _("Customers")

    def __str__(self):
        return f"{self.customer.username}"


class Address(LogicalMixin, TimeStampMixin):
    updated_at = None
    is_active = None

    customer = models.ForeignKey(Customer, verbose_name=_("Customer"), on_delete=models.CASCADE)
    province = models.CharField(verbose_name=_("Province"), max_length=100)
    city = models.CharField(verbose_name=_("City"), max_length=100)
    details = models.TextField(verbose_name=_("Details"), )
    post_code = models.CharField(verbose_name=_("Post code"), max_length=10, validators=[
        RegexValidator(
            regex='^\d{10}$',
            message='Code must be exactly 10 digits long'
        )
    ])
    has_paid_order = models.BooleanField(verbose_name=_("Used in Order"), default=False)

    def __str__(self):
        return f"{self.customer} - {self.province} - {self.city}"

    def delete(self):
        if self.has_paid_order:
            super().delete()
        else:
            super().hard_delete()

    class Meta:
        verbose_name = _("Address")
        verbose_name_plural = _("Addresses")
