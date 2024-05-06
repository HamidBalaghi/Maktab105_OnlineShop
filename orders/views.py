from django.http import JsonResponse
from django.views import View
import json
from django.views.generic import UpdateView
from core.mixin import LoginRequiredMixin, NavbarMixin
from customers.models import Customer
from orders.models import Order
from products.models import Product


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


class CartView(LoginRequiredMixin, NavbarMixin, UpdateView):
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
