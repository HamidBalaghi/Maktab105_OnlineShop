from django.contrib import admin
from products.models import Product, Image, Price, Category, Discount
from django.utils.translation import gettext as _


class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'brand', 'stock', 'is_active', 'is_deleted')
    list_filter = ('categories', 'is_active', 'is_deleted')
    search_fields = ('name', 'brand')
    ordering = ('is_deleted', 'is_active', 'brand', 'name')
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
        return Product.global_objects.all()


class ImageAdmin(admin.ModelAdmin):
    list_display = ('get_product_name', 'image', 'is_active', 'is_deleted')
    list_filter = ('product__brand', 'is_active', 'is_deleted')
    search_fields = ('product__name', 'product__brand')

    def get_product_name(self, obj):
        return f"{obj.product.brand}/{obj.product.name}"

    get_product_name.short_description = 'Product Name'

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
        return Image.global_objects.all()


class PriceRangeFilter(admin.SimpleListFilter):
    title = _('Price Range')
    parameter_name = 'price_range'

    def lookups(self, request, model_admin):
        return (
            ('0-1000000', _('0 - 1000000')),
            ('1000001-5000000', _('1000001 - 5000000')),
            ('5000001-10000000', _('5000001 - 10000000')),
            ('10000001-Max', _('10000001 -Max')),
            # Add more ranges as needed
        )

    def queryset(self, request, queryset):
        if self.value() == '0-1000000':
            return queryset.filter(price__range=(0, 1000000))
        elif self.value() == '1000001-5000000':
            return queryset.filter(price__range=(100001, 5000000))
        elif self.value() == '5000001-10000000':
            return queryset.filter(price__range=(5000001, 10000000))
        elif self.value() == '10000001-Max':
            return queryset.filter(price__gte=10000000)
        # Add more conditions for other ranges if needed
        else:
            return queryset


class PriceAdmin(admin.ModelAdmin):
    list_display = ('get_product_name', 'price', 'is_active', 'is_deleted')
    list_filter = (PriceRangeFilter, 'is_active', 'is_deleted')
    search_fields = ('product__name', 'product__brand', 'price')
    ordering = ('is_deleted', 'is_active', 'price')
    date_hierarchy = 'created_at'

    def get_product_name(self, obj):
        return f"{obj.product.brand}/{obj.product.name}"

    get_product_name.short_description = 'Product Name'

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
        return Price.global_objects.all()


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('category', 'parent', 'is_active', 'is_deleted')
    list_filter = ('is_active', 'is_deleted')
    search_fields = ('category',)
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
        return Category.global_objects.all()


class DiscountAdmin(admin.ModelAdmin):
    list_display = ('get_product_name', 'is_percent_type', 'amount', 'expiration_date', 'is_deleted')
    list_filter = ('is_percent_type', 'is_deleted', 'product__categories')
    search_fields = ('product__name', 'product__brand', 'amount')
    ordering = ('is_deleted', '-expiration_date')

    def get_product_name(self, obj):
        return f"{obj.product.brand}/{obj.product.name}"

    get_product_name.short_description = 'Product Name'

    def mark_as_category_discount(self, request, queryset):
        queryset.update(is_deleted=True)

    mark_as_category_discount.short_description = "Mark selected discounts as expired"

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
        return Discount.global_objects.all()


admin.site.register(Product, ProductAdmin)
admin.site.register(Price, PriceAdmin)
admin.site.register(Image, ImageAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Discount, DiscountAdmin)
