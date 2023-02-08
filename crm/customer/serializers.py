"""
Serializers for the customer APIs.
"""
import datetime
from rest_framework import serializers

from core.models import Customer, Contract


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


class ContractSerializer(serializers.ModelSerializer):
    """Serializer for contract objects."""
    payment_due = serializers.DateField(format="%Y-%m-%d")

    class Meta:
        model = Contract
        fields = (
                'id',
                'sales_contact',
                'customer',
                'date_created',
                'date_updated',
                'signed',
                'amount',
                'payment_due',
                'event'
                )
        read_only_fields = ('id', 'date_created', 'date_updated')

    def validate(self, data):
        """Check validation."""
        if 'payment_due' in data:
            if data['payment_due'] < datetime.date.today():
                raise serializers.ValidationError(
                    "Payment due date must be a future date.")
        if 'amount' in data:
            if data['amount'] < 0:
                raise serializers.ValidationError(
                    "Amount must be a positive number.")
        return data
