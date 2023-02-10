"""
Handle permissions for the API.
"""
from rest_framework import permissions

from core.models import User


class IsSalesOwnerOrReadOnly(permissions.BasePermission):
    """Custom permission to only allow sales to create a customer."""

    def has_permission(self, request, view):
        """Check if user is sales or read only."""
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.role == 'sales'

    def has_object_permission(self, request, view, obj):
        """Check if user is sales or read only."""
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user == obj.sales_contact


class IsSupportOwnerOrReadOnly(permissions.BasePermission):
    """Custom permission to only allow support to create an event."""

    def has_permission(self, request, view):
        """Check if user is support or read only."""
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.role == 'support'

    def has_object_permission(self, request, view, obj):
        """Check if user is support or read only."""
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user == obj.support_contact
