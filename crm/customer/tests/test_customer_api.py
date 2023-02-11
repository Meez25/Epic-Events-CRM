"""
Test for customer api.
"""
import datetime
import unittest.mock

from django.utils.timezone import make_aware
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from customer.serializers import EventSerializer

from core.models import Customer, Contract, Event

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


def create_contract_url(customer_id):
    """Return contract list URL."""
    return reverse("contract-list", args=[customer_id])


def get_contract_url(customer_id, contract_id):
    """Return contract detail URL."""
    return reverse("contract-detail", args=[customer_id, contract_id])


def get_event_url(customer_id, contract_id, event_id):
    """Return event detail URL."""
    return reverse("event-detail", args=[customer_id, contract_id, event_id])


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

    def test_sales_user_see_all_customers(self):
        """Test that sales user can see all customers."""
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
        self.assertEqual(len(res.data['results']), 3)
        self.assertEqual(res.data['results'][0]['id'], customer1.id)
        self.assertEqual(res.data['results'][1]['id'], customer2.id)
        self.assertEqual(res.data['results'][2]['id'], customer3.id)

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

    def test_sales_user_cannot_modify_an_unassigned_customer_with_put(self):
        """Test that sales user cannot modify an unassigned customer."""
        sales_user2 = get_user_model().objects.create_user(
                email='sales2@example.com',
                role='sales',
                password='testpass',
                )
        customer2 = create_customer(sales_user2, "test2@example.com")
        payload = {
                'first_name': 'Test Name',
                'last_name': 'User',
                'email': 'test2@example.com',
                'phone': '1234567890',
                'mobile': '1234567890',
                'company': 'Test Company',
                }
        url = detail_customer_url(customer2.id)
        res = self.sales_client.put(url, payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

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

    def test_sales_user_cannot_modify_an_unassigned_customer_with_patch(self):
        """Test that sales user cannot modify an unassigned customer."""
        sales_user2 = get_user_model().objects.create_user(
                email='sales2@example.com',
                role='sales',
                password='testpass',
                )
        customer2 = create_customer(sales_user2, "test2@example.com")
        payload = {
                'last_name': 'User',
                'email': 'test2@example.com',
                'company': 'Test Company',
                }
        url = detail_customer_url(customer2.id)
        res = self.sales_client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_sales_user_can_delete_his_assigned_customers(self):
        """Test that sales user can delete his assigned customers."""
        customer = create_customer(self.sales_user, "test1@example.com")
        url = detail_customer_url(customer.id)
        res = self.sales_client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        exists = Customer.objects.filter(id=customer.id).exists()
        self.assertFalse(exists)

    def test_sales_user_cannot_delete_an_unassigned_customer(self):
        """Test that sales user cannot delete an unassigned customer."""
        sales_user2 = get_user_model().objects.create_user(
                email='sales2@example.com',
                role='sales',
                password='testpass',
                )

        customer2 = create_customer(sales_user2, "test2@example.com")
        url = detail_customer_url(customer2.id)
        res = self.sales_client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        exists = Customer.objects.filter(id=customer2.id).exists()
        self.assertTrue(exists)

    def test_sales_user_is_able_to_filter_customer_by_email(self):
        """Test that sales user can filter customers by email."""
        customer1 = create_customer(self.sales_user, "test@example.com")
        customer2 = create_customer(self.sales_user, "test2@example.com")
        customer3 = create_customer(self.sales_user, "test3@example.com")
        res = self.sales_client.get(CUSTOMER_URL,
                                    {'email': 'test@example.com'})

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data['results']), 1)
        self.assertEqual(res.data['results'][0]['id'], customer1.id)
        self.assertNotIn(customer2.id, [c['id'] for c in res.data['results']])
        self.assertNotIn(customer3.id, [c['id'] for c in res.data['results']])

    def test_sales_user_is_able_to_filter_customer_by_email_weird_cap(self):
        """Test that sales user can filter customers by email."""
        customer1 = create_customer(self.sales_user, "test@example.com")
        customer2 = create_customer(self.sales_user, "test2@example.com")
        customer3 = create_customer(self.sales_user, "test3@example.com")
        res = self.sales_client.get(CUSTOMER_URL,
                                    {'email': 'TEST@example.com'})

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data['results']), 1)
        self.assertEqual(res.data['results'][0]['id'], customer1.id)
        self.assertNotIn(customer2.id, [c['id'] for c in res.data['results']])
        self.assertNotIn(customer3.id, [c['id'] for c in res.data['results']])

    def test_sales_user_is_able_to_filter_customer_by_name(self):
        """Test that sales user can filter customers by name."""
        customer1 = create_customer(self.sales_user, "test@example.com")
        customer2 = create_customer(self.sales_user, "test2@example.com")
        customer3 = create_customer(self.sales_user, "test3@example.com")
        customer4 = Customer.objects.create(
                first_name='Test',
                last_name='ToFind',
                email="test4@example.com",
                company="Test Company",
                sales_contact=self.sales_user,
                )
        res = self.sales_client.get(CUSTOMER_URL,
                                    {'name': 'ToFind'})

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data['results']), 1)
        self.assertNotIn(customer1.id, [c['id'] for c in res.data['results']])
        self.assertNotIn(customer2.id, [c['id'] for c in res.data['results']])
        self.assertNotIn(customer3.id, [c['id'] for c in res.data['results']])
        self.assertEqual(res.data['results'][0]['id'], customer4.id)

    def test_sales_user_can_create_a_contract(self):
        """Test that sales user can create a contract."""
        customer = create_customer(self.sales_user, "test@example.com")
        date_in_1_year = datetime.date.today() + datetime.timedelta(days=365)
        date_as_string_in_1_year = date_in_1_year.strftime('%Y-%m-%d')
        payload = {
                'signed': False,
                'amount': 1000.00,
                'payment_due': date_as_string_in_1_year,
                }
        url = create_contract_url(customer.id)
        res = self.sales_client.post(url, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        contract = Contract.objects.get(id=res.data['id'])
        self.assertEqual(contract.signed, payload['signed'])
        self.assertEqual(contract.amount, payload['amount'])
        self.assertEqual(contract.payment_due, date_in_1_year)
        self.assertEqual(contract.customer.id, customer.id)
        self.assertEqual(contract.sales_contact.id, self.sales_user.id)

    def test_sales_user_set_date_in_past(self):
        """Test that sales user cannot set a date in the past."""
        customer = create_customer(self.sales_user, "test@example.com")
        date_one_year_ago = (datetime.date.today() -
                             datetime.timedelta(days=365))
        date_as_string_one_year_ago = date_one_year_ago.strftime('%Y-%m-%d')
        payload = {
                'signed': False,
                'amount': 1000.00,
                'payment_due': date_as_string_one_year_ago,
                }
        url = create_contract_url(customer.id)
        res = self.sales_client.post(url, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_sales_user_creates_contract_with_no_amount(self):
        """Test that sales user cannot create a contract with no amount."""
        customer = create_customer(self.sales_user, "test@example.com")
        date_in_1_year = datetime.date.today() + datetime.timedelta(days=365)
        date_as_string_in_1_year = date_in_1_year.strftime('%Y-%m-%d')
        payload = {
                'signed': False,
                'payment_due': date_as_string_in_1_year,
                }
        url = create_contract_url(customer.id)
        res = self.sales_client.post(url, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_sales_user_creates_contract_with_negative_amount(self):
        """Test that sales user cannot create a contract with negative
        amount."""
        customer = create_customer(self.sales_user, "test@example.com")
        date_in_1_year = datetime.date.today() + datetime.timedelta(days=365)
        date_as_string_in_1_year = date_in_1_year.strftime('%Y-%m-%d')
        payload = {
                'signed': False,
                'amount': -1000.00,
                'payment_due': date_as_string_in_1_year,
                }
        url = create_contract_url(customer.id)
        res = self.sales_client.post(url, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_sales_user_creates_contract_with_bad_amount(self):
        """Test that sales user cannot create a contract with bad
        amount."""
        customer = create_customer(self.sales_user, "test@example.com")
        date_in_1_year = datetime.date.today() + datetime.timedelta(days=365)
        date_as_string_in_1_year = date_in_1_year.strftime('%Y-%m-%d')
        payload = {
                'signed': False,
                'amount': "ImBad",
                'payment_due': date_as_string_in_1_year,
                }
        url = create_contract_url(customer.id)
        res = self.sales_client.post(url, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_sales_user_creates_contract_with_int_amount(self):
        """Test that sales user cannot create a contract with int
        amount."""
        customer = create_customer(self.sales_user, "test@example.com")
        date_in_1_year = datetime.date.today() + datetime.timedelta(days=365)
        date_as_string_in_1_year = date_in_1_year.strftime('%Y-%m-%d')
        payload = {
                'signed': False,
                'amount': 1,
                'payment_due': date_as_string_in_1_year,
                }
        url = create_contract_url(customer.id)
        res = self.sales_client.post(url, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_support_user_cannot_create_a_contract(self):
        """Test that support user cannot create a contract."""
        customer = create_customer(self.support_user, "test@example.com")
        date_in_1_year = datetime.date.today() + datetime.timedelta(days=365)
        date_as_string_in_1_year = date_in_1_year.strftime('%Y-%m-%d')
        payload = {
                'signed': False,
                'amount': 1000.00,
                'payment_due': date_as_string_in_1_year,
                }
        url = create_contract_url(customer.id)
        res = self.support_client.post(url, payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_sales_user_can_get_the_contract_list(self):
        """Test that sales user can get the contract list."""
        customer = create_customer(self.sales_user, "test@example.com")
        contract1 = Contract.objects.create(
                signed=False,
                amount=1000.00,
                payment_due=(datetime.date.today() +
                             datetime.timedelta(days=365)),
                customer=customer,
                sales_contact=self.sales_user,
                )
        contract2 = Contract.objects.create(
                signed=False,
                amount=1000.00,
                payment_due=(datetime.date.today() +
                             datetime.timedelta(days=365)),
                customer=customer,
                sales_contact=self.sales_user,
                )
        url = create_contract_url(customer.id)
        res = self.sales_client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data['results']), 2)
        self.assertEqual(res.data['results'][0]['id'], contract1.id)
        self.assertEqual(res.data['results'][1]['id'], contract2.id)

    def test_sales_user_can_modify_a_contract_with_put(self):
        """Test that sales user can modify a contract."""
        customer = create_customer(self.sales_user, "test@example.com")
        contract = Contract.objects.create(
                signed=False,
                amount=1000.00,
                payment_due=(datetime.date.today() +
                             datetime.timedelta(days=365)),
                customer=customer,
                sales_contact=self.sales_user,
                )
        date_in_1_year = datetime.date.today() + datetime.timedelta(days=365)
        date_as_string_in_1_year = date_in_1_year.strftime('%Y-%m-%d')
        payload = {
                'signed': True,
                'amount': 2000.00,
                'payment_due': date_as_string_in_1_year,
                'support_contact': self.support_user.id,
                }
        url = get_contract_url(customer.id, contract.id)
        res = self.sales_client.put(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        contract.refresh_from_db()
        self.assertEqual(contract.signed, payload['signed'])
        self.assertEqual(contract.amount, payload['amount'])
        self.assertEqual(contract.payment_due, date_in_1_year)

    def test_sales_user_can_modify_a_contract_with_patch(self):
        """Test that sales user can modify a contract."""
        customer = create_customer(self.sales_user, "test@example.com")
        contract = Contract.objects.create(
                signed=False,
                amount=1000.00,
                payment_due=(datetime.date.today() +
                             datetime.timedelta(days=365)),
                customer=customer,
                sales_contact=self.sales_user,
                )
        date_in_1_year = datetime.date.today() + datetime.timedelta(days=365)
        date_as_string_in_1_year = date_in_1_year.strftime('%Y-%m-%d')
        payload = {
                'signed': True,
                'payment_due': date_as_string_in_1_year,
                'support_contact': self.support_user.id,
                }
        url = get_contract_url(customer.id, contract.id)
        res = self.sales_client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        contract.refresh_from_db()
        self.assertEqual(contract.signed, payload['signed'])
        self.assertEqual(contract.payment_due, date_in_1_year)

    def test_sales_user_can_delete_a_contract(self):
        """Test that sales user can delete a contract."""
        customer = create_customer(self.sales_user, "test@example.com")
        contract = Contract.objects.create(
                signed=False,
                amount=1000.00,
                payment_due=(datetime.date.today() +
                             datetime.timedelta(days=365)),
                customer=customer,
                sales_contact=self.sales_user,
                )
        url = get_contract_url(customer.id, contract.id)
        res = self.sales_client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Contract.objects.count(), 0)

    def test_sales_cannot_delete_anothers_contract(self):
        """Test that a sales user cannot delete another's sales contract."""
        sales_user2 = get_user_model().objects.create_user(
                email='sales2@example.com',
                role='sales',
                password='testpass',
                )
        customer = create_customer(sales_user2, "test@example.com")
        contract = Contract.objects.create(
                signed=False,
                amount=1000.00,
                payment_due=(datetime.date.today() +
                             datetime.timedelta(days=365)),
                customer=customer,
                sales_contact=sales_user2,
                )
        url = get_contract_url(customer.id, contract.id)
        res = self.sales_client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Contract.objects.count(), 1)

    def test_sales_user_can_search_contract_with_customer_name(self):
        """Test that a sales user can search contracts from a customer name"""
        customer1 = create_customer(self.sales_user, "test1@example.com")
        customer2 = Customer.objects.create(
                first_name="Test2",
                last_name="test",
                company="test company",
                email="test2@example.com",
                sales_contact=self.sales_user,
                )
        contract1 = Contract.objects.create(
                signed=False,
                amount=1000.00,
                payment_due=(datetime.date.today() +
                             datetime.timedelta(days=365)),
                customer=customer1,
                sales_contact=self.sales_user,
                )
        contract2 = Contract.objects.create(
                signed=False,
                amount=1000.00,
                payment_due=(datetime.date.today() +
                             datetime.timedelta(days=365)),
                customer=customer1,
                sales_contact=self.sales_user,
                )
        contract3 = Contract.objects.create(
                signed=False,
                amount=1000.00,
                payment_due=(datetime.date.today() +
                             datetime.timedelta(days=365)),
                customer=customer2,
                sales_contact=self.sales_user,
                )
        url = reverse('search-contract-list')
        res = self.sales_client.get(url, {'last_name': customer1.last_name})

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data["results"]), 2)
        self.assertEqual(res.data['results'][0]['id'], contract1.id)
        self.assertEqual(res.data['results'][1]['id'], contract2.id)
        self.assertNotIn(contract3.id, res.data['results'])

    def test_sales_user_can_search_contract_with_customer_email(self):
        """Test that a sales user can search contracts from a customer
        email."""
        customer1 = create_customer(self.sales_user, "test1@example.com")
        customer2 = Customer.objects.create(
                first_name="Test2",
                last_name="test",
                company="test company",
                email="test2@example.com",
                sales_contact=self.sales_user,
                )
        contract1 = Contract.objects.create(
                signed=False,
                amount=1000.00,
                payment_due=(datetime.date.today() +
                             datetime.timedelta(days=365)),
                customer=customer1,
                sales_contact=self.sales_user,
                )
        contract2 = Contract.objects.create(
                signed=False,
                amount=1000.00,
                payment_due=(datetime.date.today() +
                             datetime.timedelta(days=365)),
                customer=customer1,
                sales_contact=self.sales_user,
                )
        contract3 = Contract.objects.create(
                signed=False,
                amount=1000.00,
                payment_due=(datetime.date.today() +
                             datetime.timedelta(days=365)),
                customer=customer2,
                sales_contact=self.sales_user,
                )
        url = reverse('search-contract-list')
        res = self.sales_client.get(url, {'email': customer1.email})

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data['results']), 2)
        self.assertEqual(res.data['results'][0]['id'], contract1.id)
        self.assertEqual(res.data['results'][1]['id'], contract2.id)
        self.assertNotIn(contract3.id, res.data['results'])

    def test_sales_user_can_search_contract_with_contract_date(self):
        """Test that a sales user can search contracts from a contract date."""
        testtime = make_aware((datetime.datetime.now()
                               - datetime.timedelta(days=1)))
        customer1 = create_customer(self.sales_user, "test1@example.com")
        customer2 = Customer.objects.create(
                first_name="Test2",
                last_name="test",
                company="test company",
                email="test2@example.com",
                sales_contact=self.sales_user,
                )
        contract1 = Contract.objects.create(
                signed=False,
                amount=1000.00,
                payment_due=datetime.date.today(),
                customer=customer1,
                sales_contact=self.sales_user,
                )
        with unittest.mock.patch('django.utils.timezone.now') as mock_now:
            mock_now.return_value = testtime
            contract2 = Contract.objects.create(
                    signed=False,
                    amount=1000.00,
                    payment_due=(datetime.date.today() +
                                 datetime.timedelta(days=364)),
                    customer=customer1,
                    sales_contact=self.sales_user,
                    )
            contract3 = Contract.objects.create(
                    signed=False,
                    amount=1000.00,
                    payment_due=(datetime.date.today() +
                                 datetime.timedelta(days=365)),
                    customer=customer2,
                    sales_contact=self.sales_user,
                    )

        url = reverse('search-contract-list')
        today_date = datetime.date.today()
        today_date_as_string = today_date.strftime('%Y-%m-%d')
        res = self.sales_client.get(url, {'date': today_date_as_string})

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data['results']), 1)
        self.assertEqual(res.data['results'][0]['id'], contract1.id)
        self.assertNotIn(contract2.id, res.data['results'])
        self.assertNotIn(contract3.id, res.data['results'])

    def test_sales_user_can_search_a_contract_with_amount(self):
        """Test that a sales user can search a contract with amount."""

        customer1 = create_customer(self.sales_user, "test1@example.com")
        contract1 = Contract.objects.create(
                signed=False,
                amount=2000.00,
                payment_due=datetime.date.today(),
                customer=customer1,
                sales_contact=self.sales_user,
                )
        contract2 = Contract.objects.create(
                signed=False,
                amount=1000.00,
                payment_due=datetime.date.today(),
                customer=customer1,
                sales_contact=self.sales_user,
                )
        url = reverse('search-contract-list')
        res = self.sales_client.get(url, {'amount': 1000.00})

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data['results']), 1)
        self.assertEqual(res.data['results'][0]['id'], contract2.id)
        self.assertNotIn(contract1.id, res.data['results'])

    def test_sales_user_set_a_contract_on_signed_true_which_add_event(self):
        """Test that a sales user can set a contract on signed true which
        add an event."""
        customer = create_customer(self.sales_user, "test@example.com")
        date_in_1_year = datetime.date.today() + datetime.timedelta(days=365)
        date_as_string_in_1_year = date_in_1_year.strftime('%Y-%m-%d')
        payload = {
                'signed': True,
                'amount': 1000.00,
                'payment_due': date_as_string_in_1_year,
                'support_contact': self.support_user.id,
                }
        url = create_contract_url(customer.id)
        res = self.sales_client.post(url, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        contract = Contract.objects.get(id=res.data['id'])
        self.assertTrue(contract.signed)
        self.assertTrue(len(Event.objects.all()), 1)
        event = contract.event
        self.assertEqual(event.customer, customer)
        self.assertEqual(event.support_contact, self.support_user)

    def test_sales_user_signs_existing_contract_creates_event_patch(self):
        """Test that creates a new event when an existing contract is signed.
        """
        customer1 = create_customer(self.sales_user, "test1@example.com")
        contract1 = Contract.objects.create(
                signed=False,
                amount=2000.00,
                payment_due=datetime.date.today(),
                customer=customer1,
                sales_contact=self.sales_user,
                )
        payload = {
                'signed': True,
                'support_contact': self.support_user.id,
                }
        url = get_contract_url(customer1.id, contract1.id)
        res = self.sales_client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        contract = Contract.objects.get(id=res.data['id'])
        self.assertTrue(contract.signed)
        self.assertTrue(len(Event.objects.all()), 1)
        event = contract.event
        self.assertEqual(event.customer, customer1)
        self.assertEqual(event.support_contact, self.support_user)

    def test_sales_user_signs_existing_contract_creates_event_put(self):
        """Test that creates a new event when an existing contract is signed.
        """
        date_in_1_year = datetime.date.today() + datetime.timedelta(days=365)
        date_as_string_in_1_year = date_in_1_year.strftime('%Y-%m-%d')
        customer1 = create_customer(self.sales_user, "test1@example.com")
        contract1 = Contract.objects.create(
                signed=False,
                amount=2000.00,
                payment_due=datetime.date.today(),
                customer=customer1,
                sales_contact=self.sales_user,
                )
        payload = {
                'signed': True,
                'support_contact': self.support_user.id,
                'amount': 1000.00,
                'payment_due': date_as_string_in_1_year,
                }
        url = get_contract_url(customer1.id, contract1.id)
        res = self.sales_client.put(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        contract = Contract.objects.get(id=res.data['id'])
        self.assertTrue(contract.signed)
        self.assertTrue(len(Event.objects.all()), 1)
        event = contract.event
        self.assertEqual(event.customer, customer1)
        self.assertEqual(event.support_contact, self.support_user)

    def test_a_signed_contract_cannot_be_unsigned(self):
        """Test that a signed contract cannot be unsigned."""
        date_in_1_year = datetime.date.today() + datetime.timedelta(days=365)
        date_as_string_in_1_year = date_in_1_year.strftime('%Y-%m-%d')
        customer1 = create_customer(self.sales_user, "test@example.com")
        contract1 = Contract.objects.create(
                signed=True,
                amount=2000.00,
                payment_due=datetime.date.today(),
                customer=customer1,
                sales_contact=self.sales_user,
                )
        payload = {
                'signed': False,
                'support_contact': self.support_user.id,
                'amount': 3000.00,
                'payment_due': date_as_string_in_1_year,
                }
        url = get_contract_url(customer1.id, contract1.id)
        res = self.sales_client.put(url, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        contract1.refresh_from_db()
        self.assertTrue(contract1.signed)

    def test_a_signed_contract_cannot_be_unsigned_patch(self):
        """Test that a signed contract cannot be unsigned."""
        date_in_1_year = datetime.date.today() + datetime.timedelta(days=365)
        date_as_string_in_1_year = date_in_1_year.strftime('%Y-%m-%d')
        customer1 = create_customer(self.sales_user, "test@example.com")
        contract1 = Contract.objects.create(
                signed=True,
                amount=2000.00,
                payment_due=datetime.date.today(),
                customer=customer1,
                sales_contact=self.sales_user,
                )
        payload = {
                'signed': False,
                'support_contact': self.support_user.id,
                'payment_due': date_as_string_in_1_year,
                }
        url = get_contract_url(customer1.id, contract1.id)
        res = self.sales_client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        contract1.refresh_from_db()
        self.assertTrue(contract1.signed)

    def test_sales_user_cannot_modify_event(self):
        """Test that a sales user is not able to modify an event."""
        date_in_1_year = datetime.date.today() + datetime.timedelta(days=365)
        customer1 = create_customer(self.sales_user, "test@example.com")
        contract1 = Contract.objects.create(
                signed=True,
                amount=2000.00,
                payment_due=date_in_1_year,
                customer=customer1,
                sales_contact=self.sales_user,
                )
        event = Event.objects.create(
                customer=customer1,
                support_contact=self.support_user,
                )
        contract1.event = event
        contract1.save()
        payload = {
                'attendees': 10,
                }
        url = get_event_url(customer1.id, contract1.id, event.id)
        res = self.sales_client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Event.objects.get(id=event.id).attendees, None)

    def test_support_user_see_all_events(self):
        """Test that a support user can see all events."""
        date_in_1_year = datetime.date.today() + datetime.timedelta(days=365)
        customer1 = create_customer(self.sales_user, "test@example.com")
        contract1 = Contract.objects.create(
                signed=True,
                amount=2000.00,
                payment_due=date_in_1_year,
                customer=customer1,
                sales_contact=self.sales_user,
                )
        event = Event.objects.create(
                customer=customer1,
                support_contact=self.support_user,
                )
        contract1.event = event
        contract1.save()
        contract2 = Contract.objects.create(
                signed=True,
                amount=2000.00,
                payment_due=date_in_1_year,
                customer=customer1,
                sales_contact=self.sales_user,
                )
        event2 = Event.objects.create(
                customer=customer1,
                support_contact=self.support_user,
                )
        contract2.event = event2
        contract2.save()
        url = reverse("search-event-list")
        res = self.support_client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_support_user_can_modify_an_event_with_patch(self):
        """Test that a support user can modify an event."""
        date_in_1_year = datetime.date.today() + datetime.timedelta(days=365)
        customer1 = create_customer(self.sales_user, "test@example.com")
        contract1 = Contract.objects.create(
                signed=True,
                amount=2000.00,
                payment_due=date_in_1_year,
                customer=customer1,
                sales_contact=self.sales_user,
                )
        event = Event.objects.create(
                customer=customer1,
                support_contact=self.support_user,
                )
        contract1.event = event
        contract1.save()
        payload = {
                'attendees': 10,
                }
        url = get_event_url(customer1.id, contract1.id, event.id)
        res = self.support_client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(Event.objects.get(id=event.id).attendees, 10)

    def test_support_user_can_modify_an_event_with_put(self):
        """Test that a support user can modify an event."""
        date_in_1_year = datetime.date.today() + datetime.timedelta(days=365)
        customer1 = create_customer(self.sales_user, "test@example.com")
        contract1 = Contract.objects.create(
                signed=True,
                amount=2000.00,
                payment_due=date_in_1_year,
                customer=customer1,
                sales_contact=self.sales_user,
                )
        event = Event.objects.create(
                customer=customer1,
                support_contact=self.support_user,
                )
        contract1.event = event
        contract1.save()
        payload = {
                'attendees': 10,
                'customer': customer1.id,
                'support_contact': self.support_user.id,
                'notes': 'I am a note',
                }
        url = get_event_url(customer1.id, contract1.id, event.id)
        res = self.support_client.put(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(Event.objects.get(id=event.id).attendees, 10)

    def test_sales_user_see_all_events(self):
        """Test that a support user can see all events."""
        date_in_1_year = datetime.date.today() + datetime.timedelta(days=365)
        customer1 = create_customer(self.sales_user, "test@example.com")
        contract1 = Contract.objects.create(
                signed=True,
                amount=2000.00,
                payment_due=date_in_1_year,
                customer=customer1,
                sales_contact=self.sales_user,
                )
        event = Event.objects.create(
                customer=customer1,
                support_contact=self.support_user,
                )
        contract1.event = event
        contract1.save()
        contract2 = Contract.objects.create(
                signed=True,
                amount=2000.00,
                payment_due=date_in_1_year,
                customer=customer1,
                sales_contact=self.sales_user,
                )
        event2 = Event.objects.create(
                customer=customer1,
                support_contact=self.support_user,
                )
        contract2.event = event2
        contract2.save()
        url = reverse("search-event-list")
        res = self.sales_client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_support_user_cannot_modify_an_event_with_put_not_assigned(self):
        """Test that a support user can modify an event."""
        support_user2 = get_user_model().objects.create_user(
                email='support2@example.com',
                role='support',
                password='testpass',
                )
        date_in_1_year = datetime.date.today() + datetime.timedelta(days=365)
        customer1 = create_customer(self.sales_user, "test@example.com")
        contract1 = Contract.objects.create(
                signed=True,
                amount=2000.00,
                payment_due=date_in_1_year,
                customer=customer1,
                sales_contact=self.sales_user,
                )
        event = Event.objects.create(
                customer=customer1,
                support_contact=support_user2,
                )
        contract1.event = event
        contract1.save()
        payload = {
                'attendees': 10,
                'customer': customer1.id,
                'support_contact': self.support_user.id,
                'notes': 'I am a note',
                }
        url = get_event_url(customer1.id, contract1.id, event.id)
        res = self.support_client.put(url, payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_support_user_get_event_detail(self):
        """Test support user get detail."""
        date_in_1_year = datetime.date.today() + datetime.timedelta(days=365)
        customer1 = create_customer(self.sales_user, "test@example.com")
        contract1 = Contract.objects.create(
                signed=True,
                amount=2000.00,
                payment_due=date_in_1_year,
                customer=customer1,
                sales_contact=self.sales_user,
                )
        event = Event.objects.create(
                customer=customer1,
                support_contact=self.support_user,
                attendees=10,
                )
        contract1.event = event
        contract1.save()
        url = get_event_url(customer1.id, contract1.id, event.id)
        res = self.support_client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['attendees'], event.attendees)

    def test_search_event_by_customer_last_name(self):
        """Test that a user is able to search an event by its customer's
        last name."""
        date_in_1_year = datetime.date.today() + datetime.timedelta(days=365)
        customer1 = create_customer(self.sales_user, "test@example.com")
        contract1 = Contract.objects.create(
                signed=True,
                amount=2000.00,
                payment_due=date_in_1_year,
                customer=customer1,
                sales_contact=self.sales_user,
                )
        event = Event.objects.create(
                customer=customer1,
                support_contact=self.support_user,
                attendees=10,
                )
        contract1.event = event
        contract1.save()
        customer2 = Customer.objects.create(
                first_name='Test',
                last_name='ToFind',
                email="test4@example.com",
                company="Test Company",
                sales_contact=self.sales_user,
                )
        contract2 = Contract.objects.create(
                signed=True,
                amount=2000.00,
                payment_due=date_in_1_year,
                customer=customer2,
                sales_contact=self.sales_user,
                )
        event2 = Event.objects.create(
                customer=customer2,
                support_contact=self.support_user,
                attendees=10,
                )
        contract2.event = event2
        contract2.save()
        url = reverse("search-event-list")
        res = self.support_client.get(url, {'last_name': 'User'})

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data['results']), 1)
