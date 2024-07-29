from rest_framework import viewsets
from booking.models import Booking, Traveller, TransportationCompany, Vehicle, VehicleRoute, State, Payment
from .serializers import (
    BookingSerializer, TravellerSerializer, TransportationCompanySerializer, VehicleSerializer, 
    VehicleRouteSerializer, StateSerializer, PaymentSerializer
)

class TransportationCompanyViewSet(viewsets.ModelViewSet):
    queryset = TransportationCompany.objects.all()
    serializer_class = TransportationCompanySerializer

class VehicleViewSet(viewsets.ModelViewSet):
    queryset = Vehicle.objects.all()
    serializer_class = VehicleSerializer

class StateViewSet(viewsets.ModelViewSet):
    queryset = State.objects.all()
    serializer_class = StateSerializer

class VehicleRouteViewSet(viewsets.ModelViewSet):
    queryset = VehicleRoute.objects.all()
    serializer_class = VehicleRouteSerializer

class TravellerViewSet(viewsets.ModelViewSet):
    queryset = Traveller.objects.all()
    serializer_class = TravellerSerializer

class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer

class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
