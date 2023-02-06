"""
Serializers for the customer APIs.
"""
from rest_framework import serializers

from core.models import Customer


class CustomerSerializer(serializers.ModelSerializer):
    """Serializer for customer objects."""

    class Meta:
        model = Customer
        fields = (
                'id',
                'first_name',
                'last_name',
                'email',
                'phone',
                'mobile',
                'company',
                )
        read_only_fields = ('id',)
