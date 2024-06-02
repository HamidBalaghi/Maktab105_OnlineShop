from rest_framework import serializers
from orders.models import Order, OrderItem, DiscountCode
from customers.models import Address


class AddToOrderItemSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()


class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.SerializerMethodField()
    product_price = serializers.SerializerMethodField()
    product_discount = serializers.SerializerMethodField()
    product_description = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = ('id', 'quantity', 'product_name', 'product_price', 'product_discount', 'product_description')

    def get_product_name(self, obj):
        return f"{obj.product.brand}/{obj.product.name}"

    def get_product_price(self, obj):
        return obj.product.product_price()

    def get_product_discount(self, obj):
        return f"{obj.product.get_discount()[0]} {obj.product.get_discount()[1]}"

    def get_product_description(self, obj):
        return f"{obj.product.description}"


class OrderSerializer(serializers.ModelSerializer):
    order_items = OrderItemSerializer(many=True, read_only=True)
    order_owner = serializers.SerializerMethodField()
    order_subtotal = serializers.SerializerMethodField()
    order_discount = serializers.SerializerMethodField()
    order_total = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = ['id', 'order_owner', 'order_subtotal', 'order_discount', 'order_total', 'order_items']

    def get_order_owner(self, obj):
        return f"{obj.customer}"

    def get_order_subtotal(self, obj):
        return f"{obj.order_details()['final_order_subtotal']}"

    def get_order_discount(self, obj):
        return f"{obj.order_details()['final_order_discount']}"

    def get_order_total(self, obj):
        return f"{obj.order_details()['final_order_price']}"


class EditOrderSerializer(serializers.Serializer):
    delete_item = serializers.IntegerField(required=False)
    increase_item = serializers.IntegerField(required=False)
    decrease_item = serializers.IntegerField(required=False)
    clear_order = serializers.IntegerField(required=False)

    def validate(self, data):
        if not any(data.get(field) is not None for field in
                   ['delete_item', 'increase_item', 'decrease_item', 'clear_order']):
            raise serializers.ValidationError(
                "At least one of the fields must be provided: delete_item, increase_item, decrease_item, clear_order.")
        return data


class CheckoutAddressGETSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ['id', 'province', 'city', 'details', 'post_code']


class CheckoutPOSTSerializer(serializers.Serializer):
    selected_address = serializers.IntegerField(required=True)
    discount_code = serializers.IntegerField(required=False)
    payment = serializers.BooleanField(required=False)

    def validate_selected_address(self, address_id):
        if address_id < 1 or not Address.objects.filter(id=address_id).exists():
            raise serializers.ValidationError("Invalid address")
        return address_id

    def validate_discount_code(self, discount_code):
        if discount_code and not DiscountCode.objects.filter(code=discount_code, is_deleted=False,
                                                             is_used=False).exists():
            raise serializers.ValidationError("Invalid discount code.")
        return discount_code


class PaidOrderSerializer(serializers.ModelSerializer):
    invoice_number = serializers.SerializerMethodField()
    amount = serializers.SerializerMethodField()
    discount = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = ['id', 'invoice_number', 'amount', 'discount', 'paid_time']

    def get_invoice_number(self, obj):
        return obj.invoice_number

    def get_amount(self, obj):
        return obj.calculate_paid_order_total_prices_by_discount_code()

    def get_discount(self, obj):
        return obj.calculate_order_total_discount_by_discount_code()


class PaidOrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.SerializerMethodField()
    product_price = serializers.SerializerMethodField()
    product_discount_value = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = ('id', 'quantity', 'product_name', 'product_price', 'product_discount_value')

    def get_product_name(self, obj):
        return f"{obj.product.brand}/{obj.product.name}"

    def get_product_price(self, obj):
        return f"{obj.price.price}"

    def get_product_discount_value(self, obj):
        if obj.product_discount:
            if obj.product_discount.is_percent_type:
                return f"{obj.product_discount.amount}%"
            else:
                return f"{obj.product_discount.amount}$"
        else:
            return None


class OrderDetailSerializer(serializers.ModelSerializer):
    order_items = PaidOrderItemSerializer(many=True, read_only=True)
    invoice_number = serializers.SerializerMethodField()
    final_order_price_after_discount_code = serializers.SerializerMethodField()
    discount_of_code = serializers.SerializerMethodField()
    province = serializers.SerializerMethodField()
    city = serializers.SerializerMethodField()
    address_details = serializers.SerializerMethodField()
    post_code = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = [
            'id', 'order_items', 'invoice_number',
            'final_order_price_after_discount_code', 'discount_of_code',
            'paid_time', 'province', 'city', 'address_details', 'post_code'
        ]

    def get_invoice_number(self, obj):
        return obj.id + 1000

    def get_final_order_price_after_discount_code(self, obj):
        return obj.calculate_paid_order_total_prices_by_discount_code()

    def get_discount_of_code(self, obj):
        return obj.paid_order_details()['final_order_price'] - obj.calculate_paid_order_total_prices_by_discount_code()

    def get_province(self, obj):
        return obj.address.province

    def get_city(self, obj):
        return obj.address.city

    def get_address_details(self, obj):
        return obj.address.details

    def get_post_code(self, obj):
        return obj.address.post_code
