from rest_framework import serializers


class AddToOrderItemSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
