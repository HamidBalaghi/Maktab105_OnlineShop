from rest_framework import serializers
from orders.models import Order, OrderItem


class AddToOrderItemSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()


class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.SerializerMethodField()
    product_price = serializers.SerializerMethodField()
    product_discount = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = ('id', 'quantity', 'product_name', 'product_price', 'product_discount')

    def get_product_name(self, obj):
        return f"{obj.product.brand}/{obj.product.name}"

    def get_product_price(self, obj):
        return obj.product.product_price()

    def get_product_discount(self, obj):
        return f"{obj.product.get_discount()[0]} {obj.product.get_discount()[1]}"


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
