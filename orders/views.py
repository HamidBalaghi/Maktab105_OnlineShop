from django.http import JsonResponse
from django.shortcuts import redirect
from django.urls import reverse_lazy, reverse
from django.views import View
import json
from django.views.generic import UpdateView, TemplateView, FormView
from core.mixin import LoginRequiredMixin, NavbarMixin
from customers.models import Customer, Address
from orders.models import Order, OrderItem
from products.models import Product, Discount
from .mixin import CartInitializerMixin
from .forms import CheckoutForm
from orders.models import DiscountCode


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
                item.hard_delete()
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
                    item.hard_delete()
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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        customer = Customer.objects.get(customer=self.request.user)
        context['addresses'] = customer.addresses.filter(is_deleted=False).order_by('-created_at')
        context['order'] = self.get_order_details(customer)
        return context

    def post(self, request, *args, **kwargs):
        customer = Customer.objects.get(customer=self.request.user)
        order = Order.objects.get(customer=customer, is_paid=False, is_deleted=False)

        form = self.get_form(request.POST)
        if form.is_valid():
            address_id = form.cleaned_data.get('address')
            discount_code = form.cleaned_data.get('discount_code')

            selected_address = Address.objects.get(id=address_id)

            if discount_code:
                has_discount = True
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
                has_discount = False

            discount_of_code = order.order_details()['final_order_price'] - final_price_after_discount
            # Send needed information to template
            additional_context = {'final_order_price_after_discount_code': final_price_after_discount,
                                  'entered_discountCode': discount_code,
                                  'discount_of_code': discount_of_code,
                                  'selected_address': selected_address,
                                  'has_discount': has_discount}

            # manage payment
            if 'payment' in request.POST:

                if not selected_address.has_paid_order:
                    selected_address.has_paid_order = True
                    selected_address.save()

                order.address = selected_address
                order.is_paid = True
                if request.POST.get('discount_code'):
                    entered_discount_code = DiscountCode.objects.get(code=request.POST.get('discount_code').split()[0])
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
                return redirect(reverse_lazy('orders:cart'))  # todo: redirect to paid orders

            #  redirect checkout if clicked on 'Apply', and send needed context
            return self.render_to_response(self.get_context_data(form=form, **additional_context))

        # if form was invalid
        else:
            context = self.get_context_data(form=form)
            return self.render_to_response(context)

    def get_order_details(self, customer):
        return Order.objects.get(is_paid=False, customer=customer).order_details()

    def get_form(self, data=None):
        customer = Customer.objects.get(customer=self.request.user)
        form = CheckoutForm(data)
        form.fields['address'].choices = [(addr.id, addr) for addr in
                                          customer.addresses.filter(is_deleted=False).order_by('-created_at')]
        return form
