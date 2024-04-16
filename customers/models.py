from django.db import models
from django.db.models import UniqueConstraint, Q
from accounts.models import User
from core.models import TimeStampMixin, LogicalMixin


class Customer(LogicalMixin, TimeStampMixin):
    customer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    phone_number = models.CharField(max_length=11, unique=True, null=True, blank=True)
    customer_type = models.SmallIntegerField(default=5)

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=['customer'],
                condition=Q(is_deleted=False),
                name='unique_not_deleted_customer'
            )
        ]

    def __str__(self):
        return f"{self.customer.username}"
