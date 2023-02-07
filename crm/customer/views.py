"""
Views for the customer APIs.
"""
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.authentication import (
        TokenAuthentication,
        SessionAuthentication,
        )


from core.models import Customer

from customer import serializers
from customer import permissions


class CustomerViewSet(viewsets.ModelViewSet):
    """Manage customers in the database."""
    serializer_class = serializers.CustomerSerializer
    permission_classes = (IsAuthenticated, permissions.IsSalesOrReadOnly,
                          )
    authentication_classes = (TokenAuthentication, SessionAuthentication)
    queryset = Customer.objects.all()

    def get_queryset(self):
        return self.queryset.filter(sales_contact=self.request.user)
