"""
Views for the customer APIs.
"""
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication


from core.models import Customer

from customer import serializers


class CustomerViewSet(viewsets.ViewSet):
    """Manage customers in the database."""
    serializer_class = serializers.CustomerSerializer
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)

    def list(self, request):
        """Return a list of customers."""
        queryset = Customer.objects.all()
        serializer = serializers.CustomerSerializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request):
        """Create a new customer"""
        serializer = serializers.CustomerSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        """Retrieve a customer by id."""
        queryset = Customer.objects.all()
        customer = get_object_or_404(queryset, pk=pk)
        serializer = serializers.CustomerSerializer(customer)
        return Response(serializer.data)
