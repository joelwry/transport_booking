from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.routers import DefaultRouter
from .views import (
    TransportationCompanyViewSet, StateViewSet, TerminalsViewSet, VehicleViewSet, transportation_company_detail,transportation_company_list,state_detail,state_list,
    TravellerViewSet, MessageViewSet, BookingViewSet, PaymentViewSet
)

router = DefaultRouter()
#router.register(r'transportation-companies', TransportationCompanyViewSet)
#router.register(r'states', StateViewSet)
#router.register(r'terminals', TerminalsViewSet)
router.register(r'vehicles', VehicleViewSet)
router.register(r'travellers', TravellerViewSet)
router.register(r'messages', MessageViewSet)
router.register(r'bookings', BookingViewSet)
router.register(r'payments', PaymentViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
    path('api/transportation-companies/',transportation_company_list),
    path('api/transportation-companies/<int:pk>/', transportation_company_detail),
    path('api/states/', state_list),
    path('api/states/<int:pk>/',state_detail),
]