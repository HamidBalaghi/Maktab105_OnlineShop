from django.test import TestCase
from accounts.models import User


class TestUserModel(TestCase):
    def setUp(self):
        self.valid_email = "test@gmail.com"
        self.invalid_email = "invalid_email"
        self.valid_username = "test"
        self.invalid_username = ""

    def test_create_user(self):
        # Test creating a user with valid data
        user = User.objects.create_user(
            email=self.valid_email,
            username=self.valid_username
        )
        self.assertEqual(user.email, self.valid_email)
        self.assertEqual(user.username, self.valid_username)
        self.assertFalse(user.is_active)
        self.assertFalse(user.is_admin)
        self.assertTrue(all(hasattr(User, attr) for attr in
                            ["email", "username", "is_active", 'is_deleted', 'created_at', 'updated_at', 'password']))

    def test_create_superuser(self):
        user = User.objects.create_superuser(
            email=self.valid_email,
            username=self.valid_username
        )
        self.assertEqual(user.email, self.valid_email)
        self.assertEqual(user.username, self.valid_username)
        self.assertTrue(user.is_active)
        self.assertTrue(user.is_admin)

    def test_user_unique(self):
        with self.assertRaises(Exception):
            user = User.objects.create_user(
                email=self.invalid_email,
                username=self.valid_username
            )
            user2 = User.objects.create_user(
                email=self.invalid_email,
                username=self.valid_username
            )

    def test_soft_delete_users(self):
        User.objects.create_user(
            email=self.valid_email,
            username=self.valid_username
        ).delete()
        user = User.objects.get(email=self.valid_email)
        self.assertTrue(user.is_deleted)


    # def test_invalid_email(self):
    #     with self.assertRaises(ValidationError):
    #         user = User.objects.create_user(
    #             email=self.invalid_email,
    #             username=self.valid_username
    #         )
    #         print(f"userrrrrr=       {user}")
