"""
Database models.
"""
from django.db import models
from django.contrib.auth.models import (
        AbstractBaseUser,
        BaseUserManager,
        PermissionsMixin,
        )


class UserManager(BaseUserManager):
    """Manager for user profiles."""

    def create_user(self, email, role, password, first_name=None,
                    last_name=None, **extra_fields):
        """Create a new user profile."""
        if not email:
            raise ValueError('Users must have an email address')
        user = self.model(email=self.normalize_email(email),
                          first_name=first_name,
                          last_name=last_name, role=role, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password, first_name=None,
                         last_name=None, **extra_fields):
        """Create and save a new superuser with given details."""
        role = 'admin'
        user = self.create_user(
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                role=role,
                **extra_fields)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)

        return user


class User(AbstractBaseUser, PermissionsMixin):
    """
    Custom user model.
    """
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=255, blank=True, null=True)
    last_name = models.CharField(max_length=255, blank=True, null=True)
    role = models.CharField(max_length=255, default='management', choices=(
        ('management', 'management'),
        ('sales', 'sales'),
        ('support', 'support'),
        ))
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'

    def __str__(self):
        """
        Returns the string representation of our user.
        """
        return self.email


class Customer(models.Model):
    """Customer class to store customer details."""
    first_name = models.CharField(max_length=25)
    last_name = models.CharField(max_length=25)
    email = models.EmailField(unique=True, max_length=100)
    phone = models.CharField(max_length=20, blank=True, null=True)
    mobile = models.CharField(max_length=20, blank=True, null=True)
    company = models.CharField(max_length=250)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    sales_contact = models.ForeignKey('User', on_delete=models.SET_NULL,
                                      null=True, blank=True)


class Contract(models.Model):
    """Contract class to store contract details."""
    sales_contact = models.ForeignKey('User', on_delete=models.SET_NULL,
                                      null=True, blank=True)
    customer = models.ForeignKey('Customer', on_delete=models.SET_NULL,
                                 null=True, blank=True)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    status = models.BooleanField(default=False)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_due = models.DateField()


class Event(models.Model):
    """Event class to store information about events."""
    customer = models.ForeignKey('Customer', on_delete=models.CASCADE,
                                 null=False, blank=False)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    support_contact = models.ForeignKey('User', on_delete=models.SET_NULL,
                                        null=True, blank=True)
    event_status = models.CharField(max_length=255, default='open', choices=(
        ('open', 'open'), ('closed', 'closed')))
    attendees = models.IntegerField()
    event_date = models.DateField()
    notes = models.TextField(blank=True, null=True)
