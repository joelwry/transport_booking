from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated, IsAdminUser,AllowAny
from booking.models import TransportationCompany, State, Terminals, Vehicle, Traveller, Message, Booking, Payment, VehicleSchedule
from .serializers import (
    TransportationCompanySerializer, StateSerializer, TerminalsSerializer, VehicleScheduleSerializer, VehicleSerializer,
    TravellerSerializer, MessageSerializer, BookingSerializer, PaymentSerializer
)
from rest_framework.decorators import action
from django.utils import timezone
from datetime import timedelta

# TransportationCompany CRUD FOR ADMIN
@api_view(['GET', 'POST'])
@permission_classes([IsAdminUser])
def transportation_company_list(request):
    print('REQUEST COMIN IN')
    print(request.user)
    if request.method == 'GET':
        companies = TransportationCompany.objects.all()
        serializer = TransportationCompanySerializer(companies, many=True)
        return Response(serializer.data)
    elif request.method == 'POST':
        serializer = TransportationCompanySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAdminUser])
def transportation_company_detail(request, pk):
    try:
        company = TransportationCompany.objects.get(pk=pk)
    except TransportationCompany.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND, data={"data":None,"message":'Not found'})

    if request.method == 'GET':
        serializer = TransportationCompanySerializer(company)
        return Response(data = {"data":serializer.data})
    elif request.method == 'PUT':
        serializer = TransportationCompanySerializer(company, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'DELETE':
        company.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['GET', 'POST'])
def state_list(request):
    if request.method == 'GET':
        states = State.objects.all()
        serializer = StateSerializer(states, many=True)
        return Response(serializer.data)
    elif request.method == 'POST':
        serializer = StateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
def state_detail(request, pk):
    try:
        state = State.objects.get(pk=pk)
    except State.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = StateSerializer(state)
        return Response(serializer.data)
    elif request.method == 'PUT':
        serializer = StateSerializer(state, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'DELETE':
        state.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class TransportationCompanyViewSet(viewsets.ModelViewSet):
    queryset = TransportationCompany.objects.all()
    serializer_class = TransportationCompanySerializer

class StateViewSet(viewsets.ModelViewSet):
    queryset = State.objects.all()
    serializer_class = StateSerializer

class TerminalsViewSet(viewsets.ModelViewSet):
    queryset = Terminals.objects.all()
    serializer_class = TerminalsSerializer

class VehicleViewSet(viewsets.ModelViewSet):
    queryset = Vehicle.objects.all()
    serializer_class = VehicleSerializer

class TravellerViewSet(viewsets.ModelViewSet):
    queryset = Traveller.objects.all()
    serializer_class = TravellerSerializer

class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.action == 'create':
            self.permission_classes = [IsAuthenticated]
        else:
            self.permission_classes = [IsAdminUser]
        return super().get_permissions()

class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    @action(detail=True, methods=['post'])
    def book_seat(self, request, pk=None):
        schedule = get_object_or_404(VehicleSchedule, pk=pk)
        seats = request.data.get('seats', [])
        user = request.user
        traveller = get_object_or_404(Traveller, user=user)

        # Check seat availability
        available_seats = schedule.available_seats()
        if not all(seat in available_seats for seat in seats):
            return Response({'error': 'One or more seats are already booked'}, status=status.HTTP_400_BAD_REQUEST)

        # Create Booking
        booking = Booking.objects.create(
            customer=traveller,
            vehicle=schedule.vehicle,
            trip_type=request.data.get('trip_type', 'ONE WAY'),
            status='PENDING',
            pickup_state=schedule.pickup_state,
            destination_state=schedule.destination_state,
            number_of_seats=len(seats),
            number_of_adults=request.data.get('number_of_adults', 1),
            number_of_children_below_10=request.data.get('number_of_children_below_10', 0),
            total_cost=schedule.vehicle.price * len(seats),
            travel_date=schedule.travel_datetime,
            schedule=schedule,
            booked_seats=seats
        )

        # Redirect to payment gateway
        payment_url = process_payment(booking)
        return Response({
            'booking': BookingSerializer(booking).data,
            'payment_url': payment_url
        })

class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer

class VehicleScheduleViewSet(viewsets.ModelViewSet):
    queryset = VehicleSchedule.objects.all()
    serializer_class = VehicleScheduleSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        vehicle_id = self.request.query_params.get('vehicle_id')
        if vehicle_id:
            vehicle = Vehicle.objects.filter(id=vehicle_id).first()
            if vehicle:
                three_months_from_now = timezone.now() + timedelta(days=90)
                return VehicleSchedule.objects.filter(vehicle=vehicle, travel_datetime__lte=three_months_from_now)
        return VehicleSchedule.objects.none()

    @action(detail=True, methods=['get'])
    def available_seats(self, request, pk=None):
        schedule = self.get_object()
        return Response({'available_seats': schedule.available_seats()})
