from django.contrib import admin
from .models import Customer, Address


class CustomerAdmin(admin.ModelAdmin):
    list_display = ('customer', 'phone_number')


class AddressAdmin(admin.ModelAdmin):
    list_display = ('customer', 'province', 'city', 'post_code', 'has_paid_order')


admin.site.register(Customer, CustomerAdmin)
admin.site.register(Address)