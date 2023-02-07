"""
URL mappings for the customer app.
"""
from django.urls import path, include

from rest_framework_nested import routers

from customer import views


router = routers.SimpleRouter()
router.register(r"customer", views.CustomerViewSet, basename="customer")

urlpatterns = [
        path("", include(router.urls)),
        ]
