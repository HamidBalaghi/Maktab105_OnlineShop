from django.contrib import admin
from .models import Customer, Address


class CustomerAdmin(admin.ModelAdmin):
    list_display = ('customer', 'phone_number', 'is_deleted')
    list_filter = ('customer_type', 'is_deleted')
    search_fields = ('customer__username', 'phone_number')
    ordering = ('is_deleted', 'customer__username')
    date_hierarchy = 'created_at'

    def delete_model(self, request, obj):
        # If is_deleted is True, perform hard delete
        if obj.is_deleted:
            # print(obj.id)
            Customer.global_objects.get(id=obj.id).hard_delete()

        else:
            # Otherwise, perform soft delete by setting is_deleted=True
            obj.is_deleted = True
            obj.save()

    def delete_queryset(self, request, queryset):
        for obj in queryset:
            if obj.is_deleted:
                Customer.global_objects.get(id=obj.id).hard_delete()

            else:
                obj.is_deleted = True
                obj.save()

    def get_queryset(self, request):
        return Customer.global_objects.all()


class AddressAdmin(admin.ModelAdmin):
    list_display = ('customer', 'province', 'city', 'post_code', 'has_paid_order', 'is_deleted')
    list_filter = ('customer', 'has_paid_order', 'is_deleted')
    search_fields = ('customer__customer__username', 'province', 'city', 'post_code')
    ordering = ('is_deleted', 'customer__customer__username', '-has_paid_order', 'created_at')
    date_hierarchy = 'created_at'

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
        return Address.global_objects.all()


admin.site.register(Customer, CustomerAdmin)
admin.site.register(Address, AddressAdmin)
