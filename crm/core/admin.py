"""
Django admin customization.
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from core import models


class UserAdmin(BaseUserAdmin):
    """Define the admin pages for users."""
    ordering = ['id']
    list_display = ['email', 'role', 'first_name', 'last_name']
    fieldsets = (
            (None, {'fields': ('email', 'password', 'role')}),
            (
                _('Permissions'),
                {
                    'fields': (
                        'is_active',
                        'is_staff',
                        'is_superuser',
                        )
                    }
                ),
            (_('Important dates'), {'fields': ('last_login',)}),
            )
    readonly_fields = ('last_login',)
    add_fieldsets = (
            (None, {
                'classes': ('wide',),
                'fields': (
                    'email',
                    'password1',
                    'password2',
                    'first_name',
                    'last_name',
                    'role',
                    'is_active',
                    'is_staff',
                    'is_superuser',
                    )
                }),
            )


class CustomerAdmin(admin.ModelAdmin):
    """Define the admin pages for customers."""
    ordering = ['id']
    list_display = ['id', 'first_name', 'last_name',
                    'email', 'phone', 'company', 'sales_contact']


class ContractAdmin(admin.ModelAdmin):
    """Define the admin pages for contracts."""
    ordering = ['id']
    list_display = ['id', 'customer', 'sales_contact', 'date_created',
                    'date_updated', 'signed', 'amount',
                    'payment_due', 'event']


class EventAdmin(admin.ModelAdmin):
    """Define the admin pages for events."""
    ordering = ['id']
    list_display = ['id', 'customer', 'support_contact', 'event_closed',
                    'attendees', 'date_created', 'date_updated', 'notes']


admin.site.register(models.User, UserAdmin)
admin.site.register(models.Customer, CustomerAdmin)
admin.site.register(models.Contract, ContractAdmin)
admin.site.register(models.Event, EventAdmin)
