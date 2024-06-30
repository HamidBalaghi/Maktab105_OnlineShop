from django.core.validators import MinValueValidator
from django.db import models
from core.models import TimeStampMixin, LogicalMixin
from customers.models import Customer, Address
from django.utils import timezone
from django.core.exceptions import ValidationError
from products.models import Product, Price
from products.models import Discount as ProductDiscount
from utils.validators import validate_not_in_past
from django.db.models import UniqueConstraint, Q
from django.utils.translation import gettext_lazy as _


class Order(LogicalMixin, TimeStampMixin):
    customer = models.ForeignKey(Customer,
                                 verbose_name=_("Customer"),
                                 on_delete=models.SET_NULL, null=True,
                                 related_name='orders')
    address = models.ForeignKey(Address, verbose_name=_("Address"),
                                on_delete=models.SET_NULL,
                                null=True, blank=True,
                                related_name='orders')
    is_paid = models.BooleanField(verbose_name=_("Is paid"), default=False)
    paid_time = models.DateTimeField(verbose_name=_("Paid time"), null=True, blank=True)
    discount_code = models.ForeignKey('DiscountCode', verbose_name=_("Discount code"),
                                      null=True, on_delete=models.SET_NULL, blank=True,
                                      related_name='orders')

    def __str__(self):
        return f'{self.id}-{self.customer}'

    def clean(self):
        super().clean()
        if self.address:
            if self.address.customer != self.customer:
                raise ValidationError('Address must be related to this customer')

    class Meta:
        verbose_name = _("Order")
        verbose_name_plural = _("Orders")
        # todo: add constraint(just 1 not paid order)

    def save(self, *args, **kwargs):
        if self.is_paid and not self.paid_time:
            self.paid_time = timezone.now()
        super().save(*args, **kwargs)

    def order_details(self):  # Without Discount Code
        temp = dict()
        temp['owner'] = self.customer.full_name if self.customer.full_name else self.customer.customer.username
        temp['items'] = list()
        for order_item in self.order_items.all():
            temp['items'].append(order_item.order_item_details())

        temp['final_order_subtotal'] = self.calculate_order_total_prices('subtotal')
        temp['final_order_discount'] = self.calculate_order_total_prices('total_discount')
        temp['final_order_price'] = temp['final_order_subtotal'] - temp['final_order_discount']
        return temp

    def paid_order_details(self):
        temp = dict()
        temp['owner'] = self.customer.full_name if self.customer.full_name else self.customer.customer.username
        temp['items'] = list()
        # for order_item in self.order_items.filter(is_deleted=False):
        for order_item in self.order_items.all():
            temp['items'].append(order_item.paid_order_item_detail())
        temp['final_order_subtotal'] = self.calculate_paid_order_total_prices('subtotal')
        temp['final_order_discount'] = self.calculate_paid_order_total_prices('total_discount')
        temp['final_order_price'] = temp['final_order_subtotal'] - temp['final_order_discount']
        return temp

    def calculate_order_total_prices(self, field):
        total_price = 0
        for order_item in self.order_items.all():
            total_price += order_item.order_item_details()[field]
        return total_price

    def calculate_paid_order_total_prices(self, field):
        total_price = 0
        for order_item in self.order_items.all():
            total_price += order_item.paid_order_item_detail()[field]
        return total_price

    def final_price_after_discount_code(self, cart_type: str):
        if cart_type == 'unpaid':
            total_before_discount = self.order_details()['final_order_price']
        else:
            total_before_discount = self.paid_order_details()['final_order_price']

        if self.discount_code:
            if self.discount_code.is_percent_type:
                if (total_before_discount - (total_before_discount * (
                        1 - self.discount_code.amount / 100))) < self.discount_code.max_discount:
                    final_price_after_discount = total_before_discount * (1 - self.discount_code.amount / 100)

                else:
                    final_price_after_discount = total_before_discount - self.discount_code.max_discount

            else:
                if total_before_discount - self.discount_code.amount < 0:
                    final_price_after_discount = 0

                else:
                    final_price_after_discount = total_before_discount - self.discount_code.amount

            return round(final_price_after_discount, 2)
        return round(total_before_discount, 2)

    def calculate_paid_order_total_prices_by_discount_code(self):
        return self.final_price_after_discount_code('paid')

    def calculate_order_total_prices_by_discount_code(self):
        return self.final_price_after_discount_code('unpaid')

    def calculate_order_total_discount_by_discount_code(self):
        return round(
            self.order_details()['final_order_subtotal'] - self.calculate_order_total_prices_by_discount_code(), 2)

    @property
    def invoice_number(self):
        return self.id + 1000


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
    order = models.ForeignKey(Order,
                              verbose_name=_("Order"),
                              on_delete=models.SET_NULL, null=True,
                              related_name='order_items')
    product = models.ForeignKey(Product, verbose_name=_("Product"), on_delete=models.SET_NULL, null=True)
    quantity = models.PositiveIntegerField(verbose_name=_("Quantity"), validators=[MinValueValidator(1)])
    product_discount = models.ForeignKey(ProductDiscount,
                                         verbose_name=_("Product discount"),
                                         on_delete=models.SET_NULL, null=True, blank=True,
                                         related_name='order_items')
    price = models.ForeignKey(Price, verbose_name=_("Price"), on_delete=models.CASCADE,
                              null=True, blank=True, related_name='order_items')

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=['order', 'product'],
                condition=Q(is_deleted=False),
                name='in not deleted order item: unique product and order '
            )
        ]
        verbose_name = _("Order Item")
        verbose_name_plural = _("Order Items")

    def clean(self):
        super().clean()
        if self.product_discount and self.product_discount.product != self.product:
            raise ValidationError("Product discount product must be equal to the product.")

    def __str__(self):
        return f'{self.order} - {self.product} - {self.quantity}'

    def item_name(self):
        return f"{self.product.brand}/{self.product.name}"

    def order_item_details(self):
        temp = dict()
        temp['name'] = f"{self.product.brand}/{self.product.name}"
        temp['product_price'] = self.product.prices.first().price
        temp['product_id'] = self.product.id
        temp['discount_unit'] = self.product.prices.first().discount_amount()
        temp['quantity'] = self.quantity
        temp['subtotal'] = temp['quantity'] * temp['product_price']
        temp['total_discount'] = temp['quantity'] * temp['discount_unit']
        temp['total_price'] = temp['subtotal'] - temp['total_discount']
        temp['slug'] = self.product.slug
        return temp

    def paid_order_item_detail(self):
        temp = dict()
        temp['name'] = f"{self.product.brand}/{self.product.name}"
        temp['product_price'] = self.price.price
        temp['product_id'] = self.product.id
        if self.product_discount:
            if self.product_discount.is_percent_type:
                temp['discount_unit'] = round(
                    self.price.price - (self.price.price * (1 - self.product_discount.amount / 100)), 2)
            else:
                temp['discount_unit'] = round(self.product_discount.amount, 2)
        else:
            temp['discount_unit'] = 0
        temp['quantity'] = self.quantity
        temp['subtotal'] = temp['quantity'] * temp['product_price']
        temp['total_discount'] = temp['quantity'] * temp['discount_unit']
        temp['total_price'] = temp['subtotal'] - temp['total_discount']
        temp['slug'] = self.product.slug
        return temp


class DiscountCode(LogicalMixin, TimeStampMixin):
    code = models.CharField(verbose_name=_("Code"), max_length=15)
    is_percent_type = models.BooleanField(verbose_name=_("Is percent type"),
                                          default=True)
    amount = models.DecimalField(verbose_name=_("Amount"),
                                 max_digits=15, decimal_places=2,
                                 validators=[MinValueValidator(0.1)])
    max_discount = models.DecimalField(verbose_name=_("Max discount"),
                                       max_digits=15, decimal_places=2,
                                       validators=[MinValueValidator(1.0)])
    is_used = models.BooleanField(verbose_name=_("Is used"),
                                  default=False)
    expiration_date = models.DateField(verbose_name=_("Expiration date"),
                                       null=True, blank=True)

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
        verbose_name = _("Discount Code")
        verbose_name_plural = _("Discount Codes")
