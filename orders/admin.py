from django.contrib import admin
from orders.models import Order, OrderItem, DiscountCode

# Register your models here.

admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(DiscountCode)
