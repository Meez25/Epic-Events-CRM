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

    def create_user(self, email, first_name, last_name,
                    role, password=None, **extra_fields):
        """Create a new user profile."""
        user = self.model(email=email, first_name=first_name,
                          last_name=last_name, role=role, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user


class User(AbstractBaseUser, PermissionsMixin):
    """
    Custom user model.
    """
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    role = models.CharField(max_length=255, default='management', choices=(
        ('management', 'management'),
        ('sales', 'sales'),
        ('support', 'support'),
        ))
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'

    def get_short_name(self):
        """
        Returns the short name for the user.
        """
        return self.name

    def get_full_name(self):
        """
        Returns the full name for the user.
        """
        return self.name

    def __str__(self):
        """
        Returns the string representation of our user.
        """
        return self.email
# Create your models here.

