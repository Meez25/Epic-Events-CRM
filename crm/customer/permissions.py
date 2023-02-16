"""
Handle permissions for the API.
"""
from rest_framework import permissions


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


class IsSales(permissions.BasePermission):
    """Custom permission to only allow sales to view contracts."""

    def has_object_permission(self, request, view, obj):
        """Check if user is sales."""
        return request.user == obj.sales_contact

    def has_permission(self, request, view):
        """Check if user is sales or read only."""
        return request.user.role == 'sales'


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
