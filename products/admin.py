from django.contrib import admin
from products.models import Product, Image, Price,Category

admin.site.register(Product)
admin.site.register(Price)
admin.site.register(Image)
admin.site.register(Category)