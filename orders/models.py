from django.core.validators import MinValueValidator
from django.db import models
from core.models import TimeStampMixin, LogicalMixin
from customers.models import Customer, Address
# from django.utils import timezone
from django.core.exceptions import ValidationError
from products.models import Product
from products.models import Discount as ProductDiscount
from utils.validators import validate_not_in_past
from django.db.models import UniqueConstraint, Q


class Order(LogicalMixin, TimeStampMixin):
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, related_name='orders')
    address = models.ForeignKey(Address,
                                on_delete=models.SET_NULL,
                                null=True,
                                related_name='orders')
    is_paid = models.BooleanField(default=False)
    paid_time = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f'{self.id}-{self.customer}-{self.is_paid}'

    # def validate_address_customer_match(self):
    #     if self.address and self.address.customer != self.customer:
    #         raise ValidationError("Address does not belong to the customer.")
    #
    # def clean(self):
    #     self.validate_address_customer_match()
    #     super().clean()

    # class Meta:
    #     constraints = [
    #         models.CheckConstraint(
    #             check=models.Q(address__isnull=True) | models.Q(address__customer=models.F('customer')),
    #             name='order_address_customer_match'
    #         )
    #     ]

    # def save(self, *args, **kwargs):
    #     print(1)
    #     if self.is_paid and not self.paid_time:  # If order is being marked as paid for the first time
    #         self.paid_time = timezone.now()
    #     elif self.is_paid and self.paid_time:  # If is_paid is already True and being set again
    #         raise ValidationError("Order has already been paid.")
    #     super().save(*args, **kwargs)


class OrderItem(LogicalMixin, TimeStampMixin):
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, related_name='order_items')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    product_discount = models.ForeignKey(ProductDiscount,
                                         on_delete=models.SET_NULL, null=True, blank=True,
                                         related_name='order_items')

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=['order', 'product'],
                condition=Q(is_deleted=False),
                name='in not deleted order item: unique product and order '
            )
        ]

    def clean(self):
        super().clean()
        if self.product_discount and self.product_discount.product != self.product:
            raise ValidationError("Product discount product must be equal to the product.")

    def __str__(self):
        return f'{self.order} - {self.product} - {self.quantity}'


class DiscountCode(LogicalMixin, TimeStampMixin):
    code = models.CharField(max_length=15)
    is_percent_type = models.BooleanField(default=True)
    amount = models.DecimalField(max_digits=15, decimal_places=2, validators=[MinValueValidator(0.1)])
    max_discount = models.DecimalField(max_digits=15, decimal_places=2, validators=[MinValueValidator(1.0)])
    is_used = models.BooleanField(default=False)
    expiration_date = models.DateField(null=True, blank=True, validators=[validate_not_in_past])

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=models.Q(is_percent_type=False) | models.Q(amount__lte=100),
                name='percent type must be less than 100 '
            ),
            models.UniqueConstraint(
                fields=['code'],
                condition=models.Q(is_deleted=False),
                name='Discount code must be unique'
            )
        ]
