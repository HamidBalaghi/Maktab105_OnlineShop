from django.test import TestCase
from django.utils import timezone
from orders.models import Order, OrderItem
from products.models import Product
from products.models import Discount as ProductDiscount
from customers.models import Customer, Address


class OrderModelTest(TestCase):
    def setUp(self):
        self.customer = Customer.objects.create()
        self.address = Address.objects.create()

    def test_order_model_fields(self):
        order = Order.objects.create(customer=self.customer, address=self.address, is_paid=True,
                                     paid_time=timezone.now())
        self.assertEqual(order.customer, self.customer)
        self.assertEqual(order.address, self.address)
        self.assertTrue(order.is_paid)
        self.assertIsNotNone(order.paid_time)
        self.assertTrue(all(hasattr(Order, attr) for attr in
                            ["is_active", 'is_deleted', 'created_at', 'updated_at']))

    def test_order_model_defaults(self):
        order = Order.objects.create(customer=self.customer, address=self.address)
        self.assertFalse(order.is_paid)
        self.assertIsNone(order.paid_time)


class OrderItemModelTest(TestCase):
    def setUp(self):
        self.order = Order.objects.create()
        self.product = Product.objects.create(name='Test Product', brand='Test Brand', description='Test Description',
                                              stock=100)
        self.product_discount = ProductDiscount.objects.create(product=self.product, is_percent_type=True, amount=10.0)

    def test_order_item_model_fields(self):
        order_item = OrderItem.objects.create(order=self.order, product=self.product, quantity=2,
                                              product_discount=self.product_discount)
        self.assertEqual(order_item.order, self.order)
        self.assertEqual(order_item.product, self.product)
        self.assertEqual(order_item.quantity, 2)
        self.assertEqual(order_item.product_discount, self.product_discount)
        self.assertTrue(all(hasattr(OrderItem, attr) for attr in
                            ["is_active", 'is_deleted', 'created_at', 'updated_at']))

    def test_order_item_model_validations(self):
        # Test if quantity is greater than or equal to 1
        with self.assertRaises(Exception):
            OrderItem.objects.create(order=self.order, product=self.product, quantity=-1,
                                     product_discount=self.product_discount)
