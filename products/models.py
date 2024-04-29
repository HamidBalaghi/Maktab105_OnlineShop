from django.core.validators import MinValueValidator
from django.db import models
from django.core.exceptions import ValidationError
from core.models import TimeStampMixin, LogicalMixin
from utils.filepath import get_image_upload_path
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class Product(LogicalMixin, TimeStampMixin):
    name = models.CharField(verbose_name=_("Name"), max_length=200)
    brand = models.CharField(verbose_name=_("Brand"), max_length=200, null=True, blank=True)
    description = models.TextField(verbose_name=_("Description"), null=True, blank=True)
    stock = models.PositiveIntegerField(verbose_name=_("Stock"), )
    categories = models.ManyToManyField('Category', verbose_name=_("Categories"), related_name='products')
    slug = models.SlugField(verbose_name=_("Slug"), null=True, blank=True)

    def clean(self):
        super().clean()
        self.slug = self.name

    class Meta:
        verbose_name = _("Product")
        verbose_name_plural = _("Products")

    def __str__(self):
        return f'{self.name} - stock={self.stock}'

    def product_details(self):
        temp = dict()
        temp['name'] = self.name
        temp['brand'] = self.brand
        temp['description'] = self.description
        temp['stock'] = self.stock
        temp['categories'] = self.categories.all()
        temp['price'] = self.product_price()
        temp['final_price'] = self.final_price()
        temp['images'] = self.get_images()
        temp['discount_amount'] = self.get_discount()[0]
        temp['discount_type'] = self.get_discount()[1]
        return temp

    def get_discount(self):
        discount = self.discount.filter(is_deleted=False).first()
        if discount and discount.expiration_date >= timezone.now().date():
            if discount.is_percent_type:
                return discount.amount, '%'
            else:
                return discount.amount, '$'
        return None, None

    def product_price(self):
        return self.price.get(is_deleted=False).price

    def final_price(self):
        discount = self.discount.filter(is_deleted=False).first()
        if discount is None or discount.expiration_date < timezone.now().date():
            return round(self.product_price(), 2)
        if discount.is_percent_type:
            return round(self.product_price() * (1 - discount.amount / 100), 2)
        return round(self.product_price() - discount.amount, 2)

    def get_images(self):
        images = self.images.all()
        return images

    @property
    def get_first_image(self):
        return self.get_images().first()


class Price(LogicalMixin, TimeStampMixin):
    updated_at = None
    product = models.ForeignKey(Product,
                                verbose_name=_("Product"),
                                on_delete=models.SET_NULL, null=True,
                                related_name='price')
    price = models.DecimalField(verbose_name=_("Price"), max_digits=15, decimal_places=2)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['product'],
                condition=models.Q(is_deleted=False),
                name='Product can have just 1 price'
            )
        ]
        verbose_name = _("Price")
        verbose_name_plural = _("Prices")

    def __str__(self):
        return f'{self.product.name} - price={self.price}'


class Image(LogicalMixin, TimeStampMixin):
    product = models.ForeignKey(Product,
                                verbose_name=_("Product"),
                                on_delete=models.CASCADE,
                                related_name='images')
    image = models.ImageField(verbose_name=_("Image"),
                              upload_to=get_image_upload_path
                              )

    def __str__(self):
        return f'{self.product.brand}-{self.product.name}'

    class Meta:
        verbose_name = _('Image')
        verbose_name_plural = _('Images')


class Category(LogicalMixin, TimeStampMixin):
    category = models.CharField(verbose_name=_("Category"), max_length=200)
    parent = models.ForeignKey('self',
                               verbose_name=_("Parent"),
                               on_delete=models.SET_NULL,
                               null=True, blank=True,
                               related_name='child_categories')
    slug = models.SlugField(verbose_name=_("Slug"), null=True, blank=True)

    def clean(self):
        super().clean()
        self.slug = self.category
        if self.parent:
            if self.parent == self:
                raise ValidationError("Parent category cannot be itself.")
            if self.parent.parent == self:
                raise ValidationError("Child category cannot be the parent of its parent.")

    def __str__(self):
        if self.parent:
            return f'{self.category} - parent: {self.parent.category}'
        return f'{self.category}'

    class Meta:
        verbose_name = _("Category")
        verbose_name_plural = _("Categories")


class Discount(LogicalMixin, TimeStampMixin):
    product = models.ForeignKey(Product, verbose_name=_("Product"), on_delete=models.CASCADE, related_name='discount')
    is_percent_type = models.BooleanField(verbose_name=_("Is percent type"), default=True)
    amount = models.DecimalField(verbose_name=_("Amount"),
                                 max_digits=15, decimal_places=2,
                                 validators=[MinValueValidator(0.1)])
    expiration_date = models.DateField(verbose_name=_("Expiration date"), )

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
        verbose_name = _("Discount")
        verbose_name_plural = _("Discounts")

    def __str__(self):
        if self.is_percent_type:
            return f'{self.product.name} - {self.amount}%'
        return f'{self.product.name} - {self.amount}$'
