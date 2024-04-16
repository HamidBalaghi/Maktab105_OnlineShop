from django.db import models
from django.core.exceptions import ValidationError
from core.models import TimeStampMixin, LogicalMixin
from utils.filepath import get_image_upload_path


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
