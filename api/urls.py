from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.routers import DefaultRouter
from .views import (
    TransportationCompanyViewSet, StateViewSet, TerminalsViewSet, VehicleScheduleViewSet, VehicleViewSet, transportation_company_detail,transportation_company_list,state_detail,state_list,
    TravellerViewSet, MessageViewSet, BookingViewSet, PaymentViewSet,verifyPaymentView
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
router.register(r'vehicle-schedules', VehicleScheduleViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('transportation-companies/',transportation_company_list),
    path('transportation-companies/<int:pk>/', transportation_company_detail),
    path('states/', state_list),
    path('states/<int:pk>/',state_detail),
    path("verify-payment/<str:reference>/",verifyPaymentView,name='verify-booking-payment')
]