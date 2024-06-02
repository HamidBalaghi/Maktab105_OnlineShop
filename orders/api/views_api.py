import json
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics
from orders.models import DiscountCode
from customers.models import Address, Customer
from products.models import Product
from .serializers import AddToOrderItemSerializer, OrderSerializer, EditOrderSerializer, CheckoutAddressGETSerializer, \
    CheckoutPOSTSerializer, PaidOrderSerializer
from .mixin import CartInitializerMixinAPI
from orders.models import Order, OrderItem


class AddToOrderItem(APIView):

    def post(self, request):
        serializer = AddToOrderItemSerializer(data=request.data)
        if serializer.is_valid():
            product_id = serializer.validated_data['product_id']

            # Retrieve the existing dictionary from the cookie
            product_counts_json = request.COOKIES.get('product_counts')
            if product_counts_json:
                product_counts = json.loads(product_counts_json)
            else:
                product_counts = {}

            if product_id and product_id > 0:
                # Product capacity
                product = Product.objects.filter(id=product_id).first()
                if not product:
                    return Response({'response': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)

                product_stock = product.stock

                # Count of added products
                added_product_count = product_counts.get(str(product_id), 0)
                if product_stock > added_product_count:
                    # Increment the count for the product ID
                    product_counts[str(product_id)] = product_counts.get(str(product_id), 0) + 1

                    # Serialize the updated dictionary to a JSON string
                    product_counts_json = json.dumps(product_counts)

                    # Prepare the response message and include product details
                    message = f"{product.name} added to cart"
                    response_data = {'response': message}

                    # Add product details to the response
                    for prod_id, count in product_counts.items():
                        prod = Product.objects.get(id=prod_id)
                        response_data[prod.name] = count

                    # Set the updated dictionary in the cookie
                    response = Response(response_data)
                    response.set_cookie('product_counts', product_counts_json)
                    return response
                else:
                    return Response({'response': 'Not enough products'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({'response': 'Invalid product ID'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CartView(CartInitializerMixinAPI, APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, ]

    def get(self, request):
        try:
            order = Order.objects.get(customer__customer=request.user, is_paid=False)
        except Order.DoesNotExist:
            return Response({'error': 'Order not found'}, status=404)

        serializer = OrderSerializer(order)
        return Response(serializer.data)

    def post(self, request):
        serializer = EditOrderSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            errors = {}
            result = {}

            # Check for negative values and collect errors
            for key, value in data.items():
                if value is not None and value < 0:
                    errors[key] = f"{key} must be a non-negative integer."
                elif key == 'clear_order':
                    try:
                        order = Order.objects.get(id=value, is_paid=False)
                        if order.customer.customer.id == request.user.id:
                            for item in order.order_items.all():
                                item.hard_delete()
                            result[key] = 'Order has been cleared'
                        else:
                            raise Order.DoesNotExist
                    except Order.DoesNotExist:
                        errors[key] = 'Order not found'
                else:
                    try:
                        order_item = OrderItem.objects.get(id=value)
                        if order_item.order.customer.customer != request.user:
                            errors[key] = "Permission denied"
                        else:
                            if key == 'delete_item':
                                order_item.hard_delete()
                                result[key] = f"{order_item.item_name()} deleted successfully from order"
                            elif key == 'increase_item':
                                if order_item.product.stock > order_item.quantity:
                                    order_item.quantity += 1
                                    order_item.save()
                                    result[key] = f"{order_item.item_name()} increased successfully"
                                else:
                                    result[key] = f"Not enough stock for {order_item.item_name()}"
                            elif key == 'decrease_item':
                                if order_item.quantity > 1:
                                    order_item.quantity -= 1
                                    order_item.save()
                                    result[key] = f"{order_item.item_name()} decreased successfully"
                                else:
                                    order_item.hard_delete()
                                    result[key] = f"{order_item.item_name()} deleted successfully from order"
                            else:
                                pass
                    except OrderItem.DoesNotExist:
                        errors[key] = "Invalid order item"

            if errors:
                return Response(errors, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response(result, status=status.HTTP_200_OK)

        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CheckoutView(CartInitializerMixinAPI, APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, ]

    def get(self, request):
        try:
            order = Order.objects.get(customer__customer=request.user, is_paid=False)
        except Order.DoesNotExist:
            return Response({'error': 'Order not found'}, status=404)

        order_serializer = OrderSerializer(order)

        addresses = Address.objects.filter(customer__customer=request.user, is_deleted=False).order_by('-created_at')
        addresses_serializer_data = CheckoutAddressGETSerializer(instance=addresses, many=True)
        return Response({'Order': order_serializer.data, 'addresses': addresses_serializer_data.data})

    def post(self, request):
        serializer = CheckoutPOSTSerializer(data=request.data)
        customer = Customer.objects.get(customer=self.request.user)
        order = Order.objects.get(customer=customer, is_paid=False, is_deleted=False)

        if serializer.is_valid():
            address_id = serializer.validated_data.get('selected_address')
            discount_code = serializer.validated_data.get('discount_code')
            result = {}

            selected_address = Address.objects.get(id=address_id)
            if selected_address.customer.customer != self.request.user:
                return Response({'selected_address': 'Invalid customer ID'}, status=400)

            if discount_code:
                discount = DiscountCode.objects.get(code=discount_code)
                order_price = order.order_details()['final_order_price']
                if discount.is_percent_type:
                    if (order_price - (order_price * (1 - discount.amount / 100))) < discount.max_discount:
                        final_price_after_discount = order_price * (1 - discount.amount / 100)
                    else:
                        final_price_after_discount = order_price - discount.max_discount
                else:
                    if order_price - discount.amount < 0:
                        final_price_after_discount = 0
                    else:
                        final_price_after_discount = order_price - discount.amount
            else:
                final_price_after_discount = 0
            result['Price after discount'] = final_price_after_discount

            if serializer.validated_data.get('payment') == True and order.order_items.exists():
                if not selected_address.has_paid_order:
                    selected_address.has_paid_order = True
                    selected_address.save()

                order.address = selected_address
                order.is_paid = True

                if discount_code:
                    entered_discount_code = DiscountCode.objects.get(code=discount_code)
                    order.discount_code = entered_discount_code
                    entered_discount_code.is_used = True  # expire discount code after use
                    entered_discount_code.save()

                order.save()

                for item in order.order_items.filter(is_deleted=False):
                    item.product_discount = item.product.discounts.first()
                    item.price = item.product.prices.first()  # Saving related price of product, at the time of purchase

                    product = item.product
                    product.stock -= item.quantity  # Decrease stock of product after purchase

                    item.save()
                    product.save()
                Order.objects.create(customer=customer)  # Create a new Order after Payment

                result['Entered DiscountCode'] = discount_code
                result['Discount of code'] = order.order_details()['final_order_price'] - final_price_after_discount
                result['Selected Address'] = {
                    'province': selected_address.province,
                    'city': selected_address.city,
                    'details': selected_address.details,
                    'postal_code': selected_address.post_code
                }

            return Response(result, status=200)
        else:
            return Response(serializer.errors, status=400)


class PaidOrdersView(generics.ListAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, ]
    serializer_class = PaidOrderSerializer

    def get_queryset(self):
        return Order.global_objects.filter(is_paid=True, customer__customer=self.request.user)
