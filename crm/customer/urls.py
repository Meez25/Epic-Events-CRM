"""
URL mappings for the customer app.
"""
from django.urls import path, include

from rest_framework_nested import routers

from customer import views


router = routers.SimpleRouter()
router.register(r"customers", views.CustomerViewSet, basename="customer")

urlpatterns = [
        path("customer/", include(router.urls)),
        ]
