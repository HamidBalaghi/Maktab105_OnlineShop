from django.db import models
from core.models import TimeStampMixin, LogicalMixin
from utils.filepath import get_image_upload_path


class Product(LogicalMixin, TimeStampMixin):
    name = models.CharField(max_length=200)
    brand = models.CharField(max_length=200, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    stock = models.PositiveIntegerField()

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
