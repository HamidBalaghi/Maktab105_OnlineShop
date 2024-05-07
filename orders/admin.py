from django.contrib import admin
from orders.models import Order, OrderItem, DiscountCode
from django.utils.translation import gettext_lazy as _

from products.models import Discount


class OrderAdmin(admin.ModelAdmin):
    list_display = ('get_customer_name', 'get_customer_address', 'is_paid', 'paid_time', 'is_deleted')
    list_filter = ('is_paid', 'is_deleted')
    search_fields = ('customer__customer__username', 'address__province', 'address__city')
    readonly_fields = ('is_paid', 'paid_time',)
    ordering = ('is_deleted', '-is_paid', '-paid_time', '-created_at')
    date_hierarchy = 'created_at'

    def get_customer_address(self, obj):
        if obj.address:
            return f"{obj.address.province}/{obj.address.city}"
        return None

    get_customer_address.short_description = 'Address'

    def get_customer_name(self, obj):
        return obj.customer

    get_customer_name.short_description = 'Customer Name'

    def get_queryset(self, request):
        return Order.global_objects.all()


class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('get_order_owner', 'get_product_name', 'quantity', 'is_deleted')
    list_filter = ('is_deleted',)
    search_fields = ('order__customer__customer__username', 'product__name', 'product__brand')
    ordering = ('is_deleted', '-created_at')
    date_hierarchy = 'created_at'

    def get_order_owner(self, obj):
        return f"{obj.order.customer}"

    get_order_owner.short_description = 'Item Owner'

    def get_product_name(self, obj):
        return f"{obj.product.brand}/{obj.product.name}"

    get_product_name.short_description = 'Product'

    def delete_model(self, request, obj):
        if obj.is_deleted:
            obj.hard_delete()
        else:
            obj.is_deleted = True
            obj.save()

    def delete_queryset(self, request, queryset):
        print(1)
        for obj in queryset:
            if obj.is_deleted:
                obj.hard_delete()

            else:
                obj.is_deleted = True
                obj.save()

    def get_queryset(self, request):
        return OrderItem.global_objects.all()


class DiscountAdmin(admin.ModelAdmin):
    list_display = ('code', 'get_discount_amount', 'max_discount', 'expiration_date', 'is_used', 'is_deleted')
    list_filter = ('is_percent_type', 'is_deleted', 'is_used')
    search_fields = ('code', 'amount')
    ordering = ('is_deleted', '-is_used', 'expiration_date', 'created_at')
    date_hierarchy = 'expiration_date'

    def get_discount_amount(self, obj):
        if obj.is_percent_type:
            return f"{obj.amount} %"
        return f"{obj.amount} $"

    get_discount_amount.short_description = _("Amount")

    def delete_model(self, request, obj):
        if obj.is_deleted:
            obj.hard_delete()
        else:
            obj.is_deleted = True
            obj.save()

    def delete_queryset(self, request, queryset):
        for obj in queryset:
            if obj.is_deleted:
                obj.hard_delete()

            else:
                obj.is_deleted = True
                obj.save()

    def get_queryset(self, request):
        return DiscountCode.global_objects.all()


admin.site.register(Order, OrderAdmin)
admin.site.register(OrderItem, OrderItemAdmin)
admin.site.register(DiscountCode, DiscountAdmin)
