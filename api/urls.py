from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    TransportationCompanyViewSet, VehicleViewSet, StateViewSet, VehicleRouteViewSet, 
    TravellerViewSet, BookingViewSet, PaymentViewSet
)

router = DefaultRouter()
router.register(r'transportation_companies', TransportationCompanyViewSet)
router.register(r'vehicles', VehicleViewSet)
router.register(r'states', StateViewSet)
router.register(r'vehicle_routes', VehicleRouteViewSet)
router.register(r'travellers', TravellerViewSet)
router.register(r'bookings', BookingViewSet)
router.register(r'payments', PaymentViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
