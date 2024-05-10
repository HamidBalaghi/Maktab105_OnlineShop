import json
from products.models import Product
from .models import Order, OrderItem


class CartInitializerMixin:

    def dispatch(self, request, *args, **kwargs):

        # Get cookie
        selected_product_raw = request.COOKIES.get('product_counts')
        if selected_product_raw:
            selected_product = json.loads(selected_product_raw)

        else:
            selected_product = {}

        # Get Order and OrderItems
        order = Order.objects.get(customer__customer=request.user, is_paid=False)
        order_items = order.order_items.select_related('product').all()
        for order_item in order_items:
            if str(order_item.product.id) in selected_product:

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
            except:
                continue

        response = super().dispatch(request, *args, **kwargs)
        response.delete_cookie('product_counts')

        return response
