"""
Test for customer api.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from core.models import Customer

CUSTOMER_URL = reverse("customer-list")


def create_customer(sales_user, **params):
    """Create and return a new customer."""
    defaults = {
            'first_name': 'Test Name',
            'last_name': 'User',
            'email': 'test@example.com',
            'phone': '1234567890',
            'mobile': '1234567890',
            'company': 'Test Company',
            }
    defaults.update(params)
    return Customer.objects.create(sales_contact=sales_user, **defaults)


class PublicProductApiTests(TestCase):
    """Test the customer API (public)."""

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """Test that login is required for retrieving customers."""
        res = self.client.get(CUSTOMER_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
