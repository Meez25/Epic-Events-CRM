"""
Serializers for the customer APIs.
"""
import datetime
import logging
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.utils.timezone import make_aware

from core.models import Customer, Contract, User, Event

logger = logging.getLogger('django')


class UserSerializer(serializers.ModelSerializer):
    """Serializer for the user object."""
    class Meta:
        model = get_user_model()
        fields = ('id', 'email', 'first_name', 'last_name', 'role')
        read_only_fields = ('id',)


class CustomerSerializer(serializers.ModelSerializer):
    """Serializer for customer objects."""
    sales_contact = UserSerializer(read_only=True)

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
                'date_created',
                'date_updated',
                'sales_contact',
                )
        read_only_fields = ('id', 'date_created', 'date_updated',)

    def create(self, validated_data):
        """Create a new customer."""
        user = self.context['request'].user
        validated_data['sales_contact'] = user
        return Customer.objects.create(**validated_data)


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
                'event',
                )
        read_only_fields = ('id', 'date_created', 'date_updated',
                            'customer', 'event', 'sales_contact')

    def validate(self, data):
        """Check validation."""
        if 'payment_due' in data:
            if data['payment_due'] < datetime.date.today():
                logger.error("Payment due date is in the past.")
                raise serializers.ValidationError(
                    "Payment due date must be a future date.")
        if 'amount' in data:
            if data['amount'] < 0:
                logger.error("Amount is negative.")
                raise serializers.ValidationError(
                    "Amount must be a positive number.")
        return data

    def create(self, validated_data):
        """Create a new contract."""
        if 'signed' not in validated_data:
            validated_data['signed'] = False
        if 'support_contact' not in validated_data:
            logger.error("Support contact is required.")
            raise serializers.ValidationError(
                "Support contact is required.")
        if (validated_data['signed'] and
                validated_data['support_contact'] is not None):
            support_contact = User.objects.get(
                id=validated_data['support_contact'])
            if support_contact is None:
                logger.error("Support contact must be a valid user.")
                raise serializers.ValidationError(
                    "Support contact must be a valid user.")
            event = Event.objects.create(
                support_contact=support_contact,
                customer=validated_data['customer'],
                )
            validated_data['event'] = event
        validated_data.pop('support_contact')
        return Contract.objects.create(**validated_data)

    def update(self, instance, validated_data):
        """Update a contract."""
        if 'support_contact' in validated_data:
            support_contact = User.objects.get(
                id=validated_data['support_contact'])
            if support_contact is None:
                logger.error("Support contact must be a valid user.")
                raise serializers.ValidationError(
                    "Support contact must be a valid user.")
            if instance.event is None:
                event = Event.objects.create(
                    support_contact=support_contact,
                    customer=instance.customer,
                    )
                instance.event = event
            else:
                instance.event.support_contact = support_contact
                instance.event.save()
            validated_data.pop('support_contact')
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()
        return instance


class EventSerializer(serializers.ModelSerializer):
    """Serializer for event objects."""

    class Meta:
        model = Event
        fields = (
                'id',
                'support_contact',
                'customer',
                'date_created',
                'date_updated',
                'event_closed',
                'attendees',
                'event_date',
                'notes',
                )
        read_only_fields = ('id', 'date_created', 'date_updated',
                            'customer')

    def validate(self, data):
        """Check validation."""
        customer_pk = self.context.get('customer_pk')
        if customer_pk:
            try:
                data['customer'] = Customer.objects.get(pk=customer_pk)
            except Customer.DoesNotExist:
                raise serializers.ValidationError("Invalid customer ID.")
        if 'event_date' in data:
            if data['event_date'] < make_aware(datetime.datetime.now()):
                logger.error("Event date is in the past.")
                raise serializers.ValidationError(
                    "Event date must be a future date.")
        if 'attendees' in data:
            if data['attendees'] < 0:
                logger.error("Attendees is negative.")
                raise serializers.ValidationError(
                    "Attendees must be a positive number.")
        return data
