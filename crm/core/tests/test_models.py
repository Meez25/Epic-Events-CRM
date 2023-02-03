"""
Test for models.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model


class ModelTests(TestCase):
    """Test for models."""

    def test_create_user_management_with_email_successful(self):
        """Test creating a new user admin with an email is successful."""
        email = 'test@email.com'
        password = 'testpass123'
        first_name = 'first_name'
        last_name = 'last_name'
        role = 'management'
        user = get_user_model().objects.create_user(
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            role=role,
            )

        self.assertEqual(user.email, email)
        self.assertTrue(user.role, role)
        self.assertTrue(user.first_name, first_name)
        self.assertTrue(user.last_name, last_name)
        self.assertTrue(user.check_password(password))

    def test_create_user_sales_with_email_successful(self):
        """Test creating a new user admin with an email is successful."""
        email = 'test@email.com'
        password = 'testpass123'
        first_name = 'first_name'
        last_name = 'last_name'
        role = 'sales'
        user = get_user_model().objects.create_user(
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            role=role,
            )
        self.assertEqual(user.email, email)
        self.assertTrue(user.role, role)
        self.assertTrue(user.first_name, first_name)
        self.assertTrue(user.last_name, last_name)
        self.assertTrue(user.check_password(password))

    def test_create_user_support_with_email_successful(self):
        """Test creating a new user support with an email is successful."""
        email = 'test@email.com'
        password = 'testpass123'
        first_name = 'first_name'
        last_name = 'last_name'
        role = 'support'
        user = get_user_model().objects.create_user(
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            role=role,
            )
        self.assertEqual(user.email, email)
        self.assertTrue(user.role, role)
        self.assertTrue(user.first_name, first_name)
        self.assertTrue(user.last_name, last_name)
        self.assertTrue(user.check_password(password))

    def test_create_user_with_wrong_role(self):
        """Test creating a new user with wrong role."""
        email = 'test@email.com'
        password = 'testpass123'
        first_name = 'first_name'
        last_name = 'last_name'
        role = 'wrongrole'
        user = get_user_model().objects.create_user(
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            role=role,
            )
        self.assertEqual(user.email, email)

    def test_new_user_email_normalized(self):
        """Test the email for a new user is normalized."""
        sample_emails = [
                ['test1@EXAMPLE.com', 'test1@example.com'],
                ['Test2@Example.com', 'Test2@example.com'],
                ['TEST3@EXAMPLE.COM', 'TEST3@example.com'],
                ['test4@example.com', 'test4@example.com'],
                ]
        for email, expected in sample_emails:
            user = get_user_model().objects.create_user(
                email=email,
                password='testpass123',
                role='management',
                )
            self.assertEqual(user.email, expected)

    def test_new_user_without_email_raises_error(self):
        """Test creating user without email raises error."""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(
                email=None,
                password='testpass123',
                role='management',
                )

    def test_create_new_superuser(self):
        """Test creating a new superuser."""
        user = get_user_model().objects.create_superuser(
                email='superuser@mail.com',
                password='testpass123',
                )
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)
