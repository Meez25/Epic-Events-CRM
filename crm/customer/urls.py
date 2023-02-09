"""
URL mappings for the customer app.
"""
from django.urls import path, include

from rest_framework_nested import routers

from customer import views


router = routers.SimpleRouter()
router.register(r"customer", views.CustomerViewSet, basename="customer")
router.register(r"contract", views.ContractViewSet, basename="search-contract")

contract_router = routers.NestedSimpleRouter(router, r"customer",
                                             lookup="customer")
contract_router.register(r"contract", views.ContractViewSet)

urlpatterns = [
        path("", include(router.urls)),
        path("", include(contract_router.urls)),
        ]
