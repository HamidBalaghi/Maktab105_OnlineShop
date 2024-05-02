from django.test import TestCase
from django.core.exceptions import ValidationError
from accounts.models import User
from customers.models import Customer, Address


class TestCustomerModel(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', email='test@example.com', password='password123')

    def test_customer_model_fields(self):
        customer = Customer.objects.create(customer=self.user, phone_number='1234567890', customer_type=5)
        self.assertEqual(customer.customer, self.user)
        self.assertEqual(customer.phone_number, '1234567890')
        self.assertEqual(customer.customer_type, 5)
        self.assertTrue(all(hasattr(Customer, attr) for attr in
                            ['customer_type', "phone_number", "customer", "is_active", 'is_deleted', 'created_at',
                             'updated_at']))

    def test_unique_constraint(self):
        Customer.objects.create(customer=self.user, phone_number='1234567890', customer_type=5)
        with self.assertRaises(Exception):
            Customer.objects.create(customer=self.user, phone_number='0987654321', customer_type=3)

    def test_soft_delete_users(self):
        Customer.objects.create(customer=self.user, phone_number='1234567890', customer_type=5).delete()
        self.assertTrue(Customer.objects.count() == 0)
        self.assertTrue(Customer.global_objects.count() == 1)
        self.assertTrue(Customer.global_objects.get(customer=self.user).is_deleted)

    def test_not_required_fields(self):
        customer = Customer.objects.create(customer=self.user)
        self.assertTrue(Customer.objects.count() == 1)
        self.assertTrue(customer.phone_number is None)
        self.assertTrue(customer.customer_type == 5)


class AddressModelTest(TestCase):
    def setUp(self):
        self.customer = Customer.objects.create()

    def test_address_model_fields(self):
        address = Address.objects.create(
            customer=self.customer,
            province='Test Province',
            city='Test City',
            details='Test Address Details',
            post_code='1234567890',
            has_paid_order=True
        )
        self.assertEqual(address.customer, self.customer)
        self.assertEqual(address.province, 'Test Province')
        self.assertEqual(address.city, 'Test City')
        self.assertEqual(address.details, 'Test Address Details')
        self.assertEqual(address.post_code, '1234567890')
        self.assertTrue(address.has_paid_order)

    # def test_post_code_validator(self):
    #     # Test Invalid post code
    #     with self.assertRaises(ValidationError):
    #         Address.objects.create(
    #             customer=self.customer,
    #             province='Test Province',
    #             city='Test City',
    #             details='Test Address Details',
    #             post_code='12345',  # Invalid, less than 10 digits
    #             has_paid_order=True
    #         )
