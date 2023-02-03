"""
Test for models.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from core.models import Customer


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

    def test_create_customer(self):
        """Test creating a new customer."""
        email = 'test@email.com'
        password = 'testpass123'
        first_name = 'first_name'
        last_name = 'last_name'
        role = 'sales'
        user_sales = get_user_model().objects.create_user(
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            role=role,
            )
        customer = Customer.objects.create(
                first_name='first_name',
                last_name='last_name',
                email='customer@example.com',
                phone='123456789',
                mobile='987654321',
                company='company',
                sales_contact=user_sales,
                )
        self.assertEqual(customer.first_name, 'first_name')
        self.assertEqual(customer.last_name, 'last_name')
        self.assertEqual(customer.email, 'customer@example.com')
        self.assertEqual(customer.phone, '123456789')
        self.assertEqual(customer.mobile, '987654321')
        self.assertEqual(customer.company, 'company')
        self.assertEqual(customer.sales_contact, user_sales)
