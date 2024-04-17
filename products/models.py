from django.core.validators import MinValueValidator
from django.db import models
from django.core.exceptions import ValidationError
from core.models import TimeStampMixin, LogicalMixin
from utils.filepath import get_image_upload_path
from utils.validators import validate_not_in_past


class Product(LogicalMixin, TimeStampMixin):
    name = models.CharField(max_length=200)
    brand = models.CharField(max_length=200, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    stock = models.PositiveIntegerField()
    categories = models.ManyToManyField('Category', related_name='products')

    def __str__(self):
        return f'{self.name} - stock={self.stock}'


class Price(LogicalMixin, TimeStampMixin):
    updated_at = None
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    price = models.DecimalField(max_digits=15, decimal_places=2)

    def __str__(self):
        return f'{self.product.name} - price={self.price}'


class Image(LogicalMixin, TimeStampMixin):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(
        upload_to=get_image_upload_path
    )

    def __str__(self):
        return f'{self.product.brand}-{self.product.name}'


class Category(LogicalMixin, TimeStampMixin):
    category = models.CharField(max_length=200)
    parent = models.ForeignKey('self', on_delete=models.SET_NULL,
                               null=True, blank=True,
                               related_name='child_categories')

    def clean(self):
        super().clean()
        if self.parent:
            if self.parent == self:
                raise ValidationError("Parent category cannot be itself.")
            if self.parent.parent == self:
                raise ValidationError("Child category cannot be the parent of its parent.")

    def __str__(self):
        if self.parent:
            return f'{self.category} - parent: {self.parent.category}'
        return f'{self.category}'


class Discount(LogicalMixin, TimeStampMixin):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='discount')
    is_percent_type = models.BooleanField(default=True)
    amount = models.DecimalField(max_digits=15, decimal_places=2, validators=[MinValueValidator(0.1)])
    expiration_date = models.DateField(null=True, blank=True, validators=[validate_not_in_past])

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=models.Q(is_percent_type=False) | models.Q(amount__lte=100),
                name='percent_type_constraint'
            ),
            models.UniqueConstraint(
                fields=['product'],
                condition=models.Q(is_deleted=False),
                name='Product can have just 1 discount'
            )
        ]

    def __str__(self):
        if self.is_percent_type:
            return f'{self.product.name} - {self.amount}%'
        return f'{self.product.name} - {self.amount}$'
