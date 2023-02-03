"""
Test for the Django admin.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import Client


class AdminSiteTests(TestCase):
    """Test for admin site."""

    def setUp(self):
        """Setup."""
        self.client = Client()
        self.admin_user = get_user_model().objects.create_superuser(
                email="admin@example.com",
                password="adminpass123",
                )
        self.client.force_login(self.admin_user)
        self.management_user = get_user_model().objects.create_user(
                email="management@example.com",
                password="userpass123",
                role="management",
                )
        self.sales_user = get_user_model().objects.create_user(
                email="sales@example.com",
                password="userpass123",
                role="sales",
                )
        self.support_user = get_user_model().objects.create_user(
                email="support@example.com",
                password="userpass123",
                role="support",
                )

    def test_users_listed(self):
        """Test that users are listed on user page."""
        url = reverse("admin:core_user_changelist")
        res = self.client.get(url)

        self.assertContains(res, self.management_user.email)
        self.assertContains(res, self.sales_user.email)
        self.assertContains(res, self.support_user.email)
