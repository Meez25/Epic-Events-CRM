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


def detail_customer_url(customer_id):
    """Return customer detail URL."""
    return reverse("customer-detail", args=[customer_id])


def create_customer(sales_user, email, **params):
    """Create and return a new customer."""
    defaults = {
            'first_name': 'Test Name',
            'last_name': 'User',
            'email': email,
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


class PrivateCustomerApiTests(TestCase):
    """Test the customer API (private)."""

    def setUp(self):
        self.sales_client = APIClient()
        self.sales_user = get_user_model().objects.create_user(
                email='sales@example.com',
                role='sales',
                password='testpass',
                )
        self.sales_client.force_authenticate(self.sales_user)

        self.support_client = APIClient()
        self.support_user = get_user_model().objects.create_user(
                email='support@example.com',
                role='support',
                password='testpass',
                )
        self.support_client.force_authenticate(self.support_user)

    def test_sales_can_create_a_customer(self):
        """Test that sales can create a customer."""
        payload = {
                'first_name': 'Test Name',
                'last_name': 'User',
                'email': 'customer@example.com',
                'company': 'Test Company',
                }
        res = self.sales_client.post(CUSTOMER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        customer = Customer.objects.get(id=res.data['id'])
        for key in payload.keys():
            assert payload[key] == getattr(customer, key)

    def test_support_cannot_create_a_customer(self):
        """Test that support cannot create a customer."""
        payload = {
                'first_name': 'Test Name',
                'last_name': 'User',
                'email': 'customer@example.com',
                'company': 'Test Company',
                }
        res = self.support_client.post(CUSTOMER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_sales_user_see_his_assigned_customers(self):
        """Test that sales user can see his assigned customers."""
        customer1 = create_customer(self.sales_user, "test1@example.com")
        customer2 = create_customer(self.sales_user, "test2@example.com")
        sales_user2 = get_user_model().objects.create_user(
                email='sales2@example.com',
                role='sales',
                password='testpass',
                )
        customer3 = create_customer(sales_user2, "test3@example.com")

        res = self.sales_client.get(CUSTOMER_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 2)
        self.assertEqual(res.data[0]['id'], customer1.id)
        self.assertEqual(res.data[1]['id'], customer2.id)
        self.assertNotIn(customer3.id, [c['id'] for c in res.data])

    def test_sales_user_can_modify_his_assigned_customers_with_put(self):
        """Test that sales user can modify his assigned customers."""
        customer = create_customer(self.sales_user, "test1@example.com")
        payload = {
                'first_name': 'Test Name',
                'last_name': 'User',
                'email': 'modified@example.com',
                'phone': '1234567890',
                'mobile': '1234567890',
                'company': 'Test Company',
                }
        url = detail_customer_url(customer.id)
        res = self.sales_client.put(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        customer.refresh_from_db()
        for key in payload.keys():
            assert payload[key] == getattr(customer, key)

    def test_sales_user_can_modify_his_assigned_customers_with_patch(self):
        """Test that sales user can modify his assigned customers."""
        customer = create_customer(self.sales_user, "test1@example.com")
        payload = {
                'first_name': 'Test Name',
                'last_name': 'User',
                }
        url = detail_customer_url(customer.id)
        res = self.sales_client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        customer.refresh_from_db()
        for key in payload.keys():
            assert payload[key] == getattr(customer, key)

    def test_sales_user_can_delete_his_assigned_customers(self):
        """Test that sales user can delete his assigned customers."""
        sales_user2 = get_user_model().objects.create_user(
                email='sales2@example.com',
                role='sales',
                password='testpass',
                )

        customer = create_customer(self.sales_user, "test1@example.com")
        customer2 = create_customer(sales_user2, "test2@example.com")
        url = detail_customer_url(customer.id)
        res = self.sales_client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        exists = Customer.objects.filter(id=customer.id).exists()
        self.assertFalse(exists)

        url2 = detail_customer_url(customer2.id)
        res2 = self.sales_client.delete(url2)
        self.assertEqual(res2.status_code, status.HTTP_404_NOT_FOUND)
        exists = Customer.objects.filter(id=customer2.id).exists()
        self.assertTrue(exists)
