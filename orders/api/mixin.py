import json
from orders.models import Order, OrderItem
from products.models import Product


class CartInitializerMixinAPI:
    def initialize_request(self, request, *args, **kwargs):
        request = super().initialize_request(request, *args, **kwargs)

        # Initialize selected_product
        selected_product_raw = request.COOKIES.get('product_counts')
        if selected_product_raw:
            selected_product = json.loads(selected_product_raw)
        else:
            selected_product = {}

        # Get Order and OrderItems
        try:
            order = Order.objects.get(customer__customer=request.user, is_paid=False)
        except Order.DoesNotExist:
            order = None

        if order:
            order_items = order.order_items.select_related('product').all()
            for order_item in order_items:
                if order_item.product.stock <= 0:
                    order_item.hard_delete()
                elif str(order_item.product.id) in selected_product:
                    if order_item.quantity + selected_product[str(order_item.product.id)] >= order_item.product.stock:
                        order_item.quantity = order_item.product.stock
                    else:
                        order_item.quantity += selected_product[str(order_item.product.id)]
                    if order_item.product.is_active:
                        order_item.save()
                    else:
                        order_item.delete()
                    del selected_product[str(order_item.product.id)]
                else:
                    if order_item.quantity > order_item.product.stock:
                        order_item.quantity = order_item.product.stock
                    if order_item.product.is_active:
                        order_item.save()
                    else:
                        order_item.delete()

            for new_product_id, new_product_quantity in selected_product.items():
                try:
                    new_product = Product.objects.get(id=int(new_product_id), is_active=True)
                    product_stock = new_product.stock
                    if new_product_quantity >= product_stock:
                        OrderItem.objects.create(order=order, product=new_product, quantity=product_stock)
                    else:
                        OrderItem.objects.create(order=order, product=new_product, quantity=new_product_quantity)
                except Product.DoesNotExist:
                    continue

        request.selected_product = selected_product
        request.order = order
        return request

    def finalize_response(self, request, response, *args, **kwargs):
        response = super().finalize_response(request, response, *args, **kwargs)
        response.delete_cookie('product_counts')
        response.delete_cookie('next_url_checkout')
        return response
