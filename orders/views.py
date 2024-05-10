from django.http import JsonResponse
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views import View
import json
from django.views.generic import UpdateView, TemplateView
from core.mixin import LoginRequiredMixin, NavbarMixin
from customers.models import Customer
from orders.models import Order, OrderItem
from products.models import Product
from .mixin import CartInitializerMixin


class AddToOrderItem(View):

    def post(self, request):
        # Retrieve the existing dictionary from the cookie
        product_counts_json = request.COOKIES.get('product_counts')
        if product_counts_json:
            product_counts = json.loads(product_counts_json)
        else:
            product_counts = {}

        # Example product ID to be incremented
        product_id = request.POST.get('product_id')
        if product_id and product_id.isnumeric() and int(product_id) > 0:
            # product capacity
            product = Product.objects.filter(id=product_id).first()
            if not product:
                return JsonResponse({'response': 'Product ID not provided'})

            product_stock = product.stock

            # count of added products
            added_product_count = product_counts.get(product_id, 0)
            if product_stock > added_product_count:
                # Increment the count for the product ID
                product_counts[product_id] = product_counts.get(product_id, 0) + 1

                # Serialize the updated dictionary to a JSON string
                product_counts_json = json.dumps(product_counts)

                # Set the updated dictionary in the cookie
                message = f"{product.name} added to card"
                response = JsonResponse({'response': message})
                response.set_cookie('product_counts', product_counts_json)
                return response
            else:
                return JsonResponse({'response': 'Not enough products'})
        else:
            return JsonResponse({'response': 'Product ID not provided'})


class CartView(LoginRequiredMixin, CartInitializerMixin, NavbarMixin, UpdateView):
    template_name = 'orders/cart.html'
    model = Order
    context_object_name = 'order'
    fields = '__all__'

    def get_object(self):
        customer = Customer.objects.get(customer=self.request.user)
        return Order.objects.get(is_paid=False, customer=customer)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['order'] = self.get_object().order_details()
        return context

    def post(self, request, *args, **kwargs):
        order = self.get_object()

        # Take user's request
        user_request = list(request.POST)[1]

        # Take product ID , if request was 'delete', 'decrease' or 'increase'
        if (dict(request.POST)[user_request][0]).isnumeric():
            product_id = dict(request.POST)[user_request][0]

        if user_request == 'deleteItem':
            try:
                item = OrderItem.objects.get(order=order, product_id=int(product_id), is_deleted=False)
                item.delete()
                response_message = f"{item.product.brand}/{item.product.name} successfully deleted"
                return JsonResponse({'response': response_message})
            except:
                pass

        elif user_request == 'decrease':
            try:
                item = OrderItem.objects.get(order=order, product_id=int(product_id), is_deleted=False)
                if item.quantity > 1:
                    item.quantity -= 1
                    item.save(update_fields=["quantity"])
                    response_message = f"{item.product.brand}/{item.product.name} decreased"
                    return JsonResponse({'response': response_message})
                else:
                    item.delete()
                    response_message = f"{item.product.brand}/{item.product.name} removed from cart"
                    return JsonResponse({'response': response_message})
            except:
                pass

        elif user_request == 'increase':
            try:
                item = OrderItem.objects.get(order=order, product_id=int(product_id), is_deleted=False)
                if item.quantity + 1 <= item.product.stock:
                    item.quantity += 1
                    item.save(update_fields=["quantity"])
                    response_message = f"{item.product.brand}/{item.product.name} increased"
                    return JsonResponse({'response': response_message})
                else:
                    response_message = f"Not enough {item.product.brand}/{item.product.name}"
                    return JsonResponse({'response': response_message})
            except:
                pass

        elif user_request == 'clearOrder':
            # Hard Delete
            order.order_items.all().delete()
            response_message = 'Order has been cleared'
            return JsonResponse({'response': response_message})

        elif user_request == 'payment':
            pass  # ToDo: config payment

        response = super().post(request, *args, **kwargs)
        return response


class CheckoutView(LoginRequiredMixin, CartInitializerMixin, NavbarMixin, TemplateView):
    template_name = 'orders/checkout-cart.html'

    def get_object(self):
        customer = Customer.objects.get(customer=self.request.user)
        return Order.objects.get(is_paid=False, customer=customer)

    def get_context_data(self, **kwargs):
        customer = Customer.objects.get(customer=self.request.user)

        context = super().get_context_data(**kwargs)
        context['order'] = self.get_object().order_details()
        context['addresses'] = customer.addresses.filter(is_deleted=False).order_by('-created_at')
        return context

    def post(self, request, *args, **kwargs):
        # print(request.POST)
        #
        # return redirect(reverse_lazy('orders:checkout'))
        pass
