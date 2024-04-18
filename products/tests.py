from django.test import TestCase
from products.models import Product, Category, Price, Discount
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta


class ProductModelTest(TestCase):
    def test_product_model_fields(self):
        product = Product.objects.create(
            name='Test Product',
            brand='Test Brand',
            description='Test Description',
            stock=100
        )
        self.assertEqual(product.name, 'Test Product')
        self.assertEqual(product.brand, 'Test Brand')
        self.assertEqual(product.description, 'Test Description')
        self.assertEqual(product.stock, 100)
        self.assertTrue(all(hasattr(Product, attr) for attr in
                            ["is_active", 'is_deleted', 'created_at', 'updated_at', 'name',
                             "brand", "description", "stock"]))

    def test_product_categories_relationship(self):
        category1 = Category.objects.create(category='Category 1')
        category2 = Category.objects.create(category='Category 2')

        product = Product.objects.create(
            name='Test Product',
            brand='Test Brand',
            description='Test Description',
            stock=100
        )
        product.categories.add(category1)
        product.categories.add(category2)

        self.assertIn(category1, product.categories.all())
        self.assertIn(category2, product.categories.all())


class PriceModelTest(TestCase):
    def setUp(self):
        self.product = Product.objects.create(name='Test Product', brand='Test Brand', description='Test Description',
                                              stock=100)

    def test_price_model_fields(self):
        price = Price.objects.create(product=self.product, price=10.99)
        self.assertEqual(price.product, self.product)
        self.assertEqual(price.price, 10.99)
        self.assertTrue(all(hasattr(Price, attr) for attr in
                            ["is_active", 'is_deleted', 'created_at', 'product', 'price']))

    def test_price_model_relationship(self):
        price = Price.objects.create(product=self.product, price=10.99)

        self.assertEqual(price.product, self.product)
        self.assertIn(price, self.product.price_set.all())


class CategoryModelTest(TestCase):
    def test_category_model_fields(self):
        category = Category.objects.create(category='Test Category')
        self.assertEqual(category.category, 'Test Category')
        self.assertIsNone(category.parent)
        self.assertTrue(all(hasattr(Category, attr) for attr in
                            ["is_active", 'is_deleted', 'created_at', 'category', 'parent']))

    def test_parent_category_relationship(self):
        parent_category = Category.objects.create(category='Parent Category')
        child_category = Category.objects.create(category='Child Category', parent=parent_category)

        self.assertEqual(child_category.parent, parent_category)
        self.assertIn(child_category, parent_category.child_categories.all())

    #
    def test_clean_method(self):
        # with self.assertRaises(Exception):
        #     category = Category(category='Test Category')
        #     category.parent = category
        #     print('dsadsadas',category.parent)

        parent_category = Category.objects.create(category='Parent Category')
        with self.assertRaises(Exception):
            child_category = Category.objects.create(category='Child Category', parent=parent_category)
            parent_category.parent = child_category
            parent_category.clean()


class DiscountModelTest(TestCase):
    def setUp(self):
        self.product = Product.objects.create(name='Test Product', brand='Test Brand', description='Test Description',
                                              stock=100)

    def test_discount_model_fields(self):
        discount = Discount.objects.create(product=self.product, is_percent_type=True, amount=10.0,
                                           expiration_date=None)
        self.assertEqual(discount.product, self.product)
        self.assertTrue(discount.is_percent_type)
        self.assertEqual(discount.amount, 10.0)
        self.assertIsNone(discount.expiration_date)

    def test_discount_model_constraints(self):
        with self.assertRaises(Exception):
            discount = Discount.objects.create(product=self.product, is_percent_type=True, amount=500.0)

    def test_discount_model_unique(self):
        with self.assertRaises(Exception):
            discount = Discount.objects.create(product=self.product, is_percent_type=True, amount=50.0)
            discount2 = Discount.objects.create(product=self.product, is_percent_type=True, amount=50.0)

    # def test_expiration_date_not_in_past(self):  ## discount not in past !!!
    #     with self.assertRaises(Exception):
    #         discount = Discount.objects.create(product=self.product,
    #                                            expiration_date=(timezone.now().date() - timedelta(days=1)), amount=50.0)

    # def test_discount_model_constraints2(self):  ##amount validator !!!
    #     with self.assertRaises(Exception):
    #         discount = Discount.objects.create(product=self.product, is_percent_type=False, amount=0.01)
