"""
Tests for the user API.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient, APITestCase
from rest_framework import status

TOKEN_URL = reverse("login")


def create_user(**params):
    return get_user_model().objects.create_user(**params)


class PublicUserApiTests(TestCase):
    """Test the users API (public)."""

    def setUp(self):
        self.client = APIClient()

    def test_create_token_for_user(self):
        """Test generates token for valid credentials."""
        user_details = {
                'first_name': 'Test Name',
                'last_name': 'User',
                'email': 'test@example.com',
                'password': 'password123',
                'role': 'sales',
                }
        create_user(**user_details)

        payload = {
                'email': user_details['email'],
                'password': user_details['password'],
                }
        res = self.client.post(TOKEN_URL, payload)

        self.assertIn('refresh', res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_token_bad_credentials(self):
        """Test token not generated for invalid credentials."""
        user_details = {
                'first_name': 'Test Name',
                'last_name': 'User',
                'email': 'test@example.com',
                'password': 'password123',
                'role': 'sales',
                }
        create_user(**user_details)
        payload = {
                'email': user_details['email'],
                'password': 'wrong-password',
                }
        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('refresh', res.data)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class JWTAuthenticationTestCase(APITestCase):
    def test_get_token(self):
        """
        Test that controls the implementation of the JWT Authentication.
        A pair of token is created and the token is testing with the
        verify endpoint.
        """
        user_details = {
                'first_name': 'Test Name',
                'last_name': 'User',
                'email': 'test@example.com',
                'password': 'password123',
                'role': 'sales',
                }
        create_user(**user_details)
        response = self.client.post(TOKEN_URL, {"email": "test@example.com",
                                                "password": "password123"},
                                    format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('access' in response.data)
        token = response.data['access']
        verify_url = reverse('verify')
        response = self.client.post(verify_url, {"token": token},
                                    format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.post(verify_url, {"token": "whatever"},
                                    format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
