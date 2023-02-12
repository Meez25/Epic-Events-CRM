"""
Views for the customer APIs.
"""
import datetime
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import (
        IsAuthenticated,
        IsAdminUser,
        )
from rest_framework.authentication import (
        TokenAuthentication,
        SessionAuthentication,
        )


from core.models import Customer, Contract, Event

from customer import serializers
from customer import permissions


class CustomerViewSet(viewsets.ModelViewSet):
    """Manage customers in the database."""
    serializer_class = serializers.CustomerSerializer
    permission_classes = (IsAuthenticated, permissions.IsSalesOwnerOrReadOnly,
                          )
    authentication_classes = (TokenAuthentication, SessionAuthentication)
    queryset = Customer.objects.all()

    def get_queryset(self):
        return self.queryset.all()

    def list(self, request, *args, **kwargs):
        """Return a list of customers."""
        email = request.query_params.get('email', None)
        if email is not None:
            self.queryset = self.queryset.filter(email__iexact=email)
        name = request.query_params.get('name', None)
        if name is not None:
            self.queryset = self.queryset.filter(
                    last_name__icontains=name
                    )
        if request.user.role == 'support':
            self.queryset = self.queryset.filter(
                    event__support_contact=request.user)
        return super().list(request, *args, **kwargs)


class ContractViewSet(viewsets.ModelViewSet):
    """Manage contracts in the database."""
    serializer_class = serializers.ContractSerializer
    permission_classes = (IsAuthenticated, permissions.IsSalesOwnerOrReadOnly,
                          )
    authentication_classes = (TokenAuthentication, SessionAuthentication)
    queryset = Contract.objects.all()

    def get_queryset(self):
        return self.queryset.all()

    def list(self, request, *args, **kwargs):
        """Return a list of contracts."""
        email = request.query_params.get('email', None)
        if email is not None:
            self.queryset = self.queryset.filter(customer__email__iexact=email)
        last_name = request.query_params.get('last_name', None)
        if last_name is not None:
            self.queryset = self.queryset.filter(
                    customer__last_name__icontains=last_name
                    )
        date = request.query_params.get('date', None)
        if date is not None:
            date_obj = datetime.datetime.strptime(date, "%Y-%m-%d")
            self.queryset = self.queryset.filter(
                    date_created__date=date_obj
                    )
        amount = request.query_params.get('amount', None)
        if amount is not None:
            try:
                amount = float(amount)
            except ValueError:
                return Response(
                        {'error': 'Invalid amount'},
                        status=status.HTTP_400_BAD_REQUEST
                        )
            self.queryset = self.queryset.filter(
                    amount__range=(amount-100, amount+100)
                    )
        return super().list(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        """Create a contract."""
        customer = Customer.objects.get(id=self.kwargs['customer_pk'])
        support_contact = request.data.get('support_contact', None)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(sales_contact=request.user, customer=customer,
                        support_contact=support_contact)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED,
                        headers=headers)

    def partial_update(self, request, *args, **kwargs):
        """Update a contract."""
        contract = self.get_object()
        signed = request.data.get('signed', None)
        support_contact = request.data.get('support_contact', None)
        if signed and contract.signed is False and support_contact is not None:
            serializer = self.get_serializer(contract, data=request.data,
                                             partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save(support_contact=support_contact)
        elif not signed and contract.signed:
            return Response(
                    {'error': 'You cannot unsign a contract.'},
                    status=status.HTTP_400_BAD_REQUEST
                    )
        elif not signed:
            serializer = self.get_serializer(contract, data=request.data,
                                             partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
        else:
            return Response(
                    {'error': 'To sign a contract, you must provide a support contact.'},
                    status=status.HTTP_400_BAD_REQUEST
                    )
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        """Update a contract."""
        contract = self.get_object()
        signed = request.data.get('signed', None)
        if type(signed) is not bool:
            return Response(
                    {'error': 'Invalid signed value.'},
                    status=status.HTTP_400_BAD_REQUEST
                    )
        support_contact = request.data.get('support_contact', None)
        if signed and contract.signed is False and support_contact is not None:
            serializer = self.get_serializer(contract, data=request.data,
                                             )
            serializer.is_valid(raise_exception=True)
            serializer.save(support_contact=support_contact)
        elif not signed and contract.signed:
            return Response(
                    {'error': 'You cannot unsign a contract.'},
                    status=status.HTTP_400_BAD_REQUEST
                    )
        elif not signed:
            serializer = self.get_serializer(contract, data=request.data,
                                             )
            serializer.is_valid(raise_exception=True)
            serializer.save()
        else:
            return Response(
                    {'error': 'To sign a contract, you must provide a support contact.'},
                    status=status.HTTP_400_BAD_REQUEST
                    )
        return Response(serializer.data)


class EventViewSet(viewsets.ModelViewSet):
    """Manage events in the database."""

    serializer_class = serializers.EventSerializer
    permission_classes = (IsAuthenticated,
                          permissions.IsSupportOwnerOrReadOnly,
                          )
    authentication_classes = (TokenAuthentication, SessionAuthentication)
    queryset = Event.objects.all()

    def get_queryset(self):
        return self.queryset.all()

    def list(self, request, *args, **kwargs):
        """Return a list of events."""
        email = request.query_params.get('email', None)
        if email is not None:
            self.queryset = self.queryset.filter(
                    contract__customer__email__iexact=email
                    )
        last_name = request.query_params.get('last_name', None)
        if last_name is not None:
            self.queryset = self.queryset.filter(
                    contract__customer__last_name__icontains=last_name
                    )
        date = request.query_params.get('date', None)
        if date is not None:
            date_obj = datetime.datetime.strptime(date, "%Y-%m-%d")
            self.queryset = self.queryset.filter(
                    event_date__date=date_obj
                    )

        return super().list(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        """Update an event."""
        event = self.get_object()
        if event.event_closed:
            return Response(
                    {'error': 'You cannot update a completed event.'},
                    status=status.HTTP_400_BAD_REQUEST
                    )
        serializer = self.get_serializer(event, data=request.data,
                                         partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
