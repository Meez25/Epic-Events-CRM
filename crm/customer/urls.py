"""
URL mappings for the customer app.
"""
from django.urls import path, include

from rest_framework_nested import routers

from customer import views


router = routers.SimpleRouter()
router.register(r"customer", views.CustomerViewSet, basename="customer")
router.register(r"contract", views.ContractViewSet, basename="search-contract")
router.register(r"event", views.EventViewSet, basename="search-event")

contract_router = routers.NestedSimpleRouter(router, r"customer",
                                             lookup="customer")
contract_router.register(r"contract", views.ContractViewSet)


event_router = routers.NestedSimpleRouter(contract_router, r"contract",
                                          lookup="contract")
event_router.register(r"event", views.EventViewSet)

urlpatterns = [
        path("", include(router.urls)),
        path("", include(contract_router.urls)),
        path("", include(event_router.urls)),
        ]
