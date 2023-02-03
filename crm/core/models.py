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
