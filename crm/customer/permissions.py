"""
Handle permissions for the API.
"""
from rest_framework import permissions

from core.models import User


class IsSalesOrReadOnly(permissions.BasePermission):
    """Custom permission to only allow sales to create a customer."""

    def has_permission(self, request, view):
        """Check if user is sales or read only."""
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.role == 'sales'
