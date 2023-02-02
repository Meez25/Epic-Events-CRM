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
