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
                is_staff=True,
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

    def test_edit_user_page(self):
        """Test that the user edit page works."""
        url = reverse("admin:core_user_change", args=[self.management_user.id])
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)

    def test_create_user_page(self):
        """Test that the user create page works."""
        url = reverse("admin:core_user_add")
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)

    def test_authorized_user_can_access_admin_site(self):
        """Test that authorized user can access admin site."""
        management_client = Client()
        management_client.force_login(self.management_user)
        url = reverse("admin:index")
        res = management_client.get(url)

        self.assertEqual(res.status_code, 200)

    def test_unauthorized_user_cannot_access_admin_site_support(self):
        """Test that unauthorized user cannot access admin site."""
        support_client = Client()
        support_client.force_login(self.support_user)
        url = reverse("admin:index")
        res = support_client.get(url)

        self.assertEqual(res.status_code, 302)

    def test_unauthorized_user_cannot_access_admin_site_sales(self):
        """Test that unauthorized user cannot access admin site."""
        sales_client = Client()
        sales_client.force_login(self.sales_user)
        url = reverse("admin:index")
        res = sales_client.get(url)

        self.assertEqual(res.status_code, 302)
