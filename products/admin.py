from django.contrib import admin
from products.models import Product, Image, Price

admin.site.register(Product)
admin.site.register(Price)
admin.site.register(Image)
