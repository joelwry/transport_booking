from django.http import HttpResponseRedirect, HttpRequest
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from booking.models import GuestBooking, GuestPayment, TransportationCompany, State, Terminals, Vehicle, Traveller, Message, Booking, Payment, VehicleSchedule
from .serializers import (
    GuestBookingSerializer, GuestPaymentSerializer, TransportationCompanySerializer, StateSerializer, TerminalsSerializer, VehicleScheduleSerializer, VehicleSerializer,
    TravellerSerializer, MessageSerializer, BookingSerializer, PaymentSerializer
)
from rest_framework.decorators import action
from django.utils import timezone
from datetime import timedelta
from .utils.payment_gateway import initiate_payment, process_payment, verify_payment
from .utils.seats_handler import calculateNumbersOfPassegers as passengerCount



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
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=['post'])
    def book_seat(self, request, pk=None):
        schedule = get_object_or_404(VehicleSchedule, pk=pk)
        seats = request.data.get('seats', [])
        user = request.user
        traveller = get_object_or_404(Traveller, user=user)
        adult_count = request.data.get('number_of_adults', 1)
        children_count = request.data.get('number_of_children_below_10', 0)
        passenger_count = passengerCount(adult_count,children_count)

        if passenger_count > len(seats) :
            return Response(
                {'error': 'Passenger boarding this vehicle is more than the seats booked'},
                status=status.HTTP_406_NOT_ACCEPTABLE
            )
        # Check seat availability
        available_seats = schedule.available_seats()
        if not all(seat in available_seats for seat in seats):
            return Response({'error': 'One or more seats are already booked'}, status=status.HTTP_410_GONE)

        trip_type = request.data.get('trip_type', 'ONE WAY')
        amount_to_pay = schedule.vehicle.price * len(seats) if trip_type == "ONE WAY" else  2 * schedule.vehicle.price * len(seats) 
        # Create Booking
        booking = Booking.objects.create(
            customer=traveller,
            vehicle=schedule.vehicle,
            trip_type=trip_type,
            status='PENDING',
            pickup_state=schedule.pickup_state,
            destination_state=schedule.destination_state,
            number_of_seats=len(seats),
            number_of_adults=adult_count,
            number_of_children_below_10=children_count,
            total_cost= amount_to_pay,
            travel_date=schedule.travel_datetime,
            schedule=schedule,
            booked_seats=seats
        )

        # Redirect to payment gateway
        payment_detail = initiate_payment(booking.booking_code,booking.total_cost, request.user.email)
        if payment_detail['success']:
            payment_url = payment_detail['payment_url']
            access_code = payment_detail['access_code']
            url = reverse('payment', args=[booking.booking_code,access_code,booking.total_cost*100])
            #return HttpResponseRedirect(url)
            return Response({
                'payment_url': payment_url,
                'booking_code': booking.booking_code,
                'access_code' : access_code,
                'total_amount': booking.total_cost
            }, status=status.HTTP_201_CREATED) 
        else :
            booking.delete()
            return Response({
                'message': payment_detail['error'] 
            }, status = status.HTTP_402_PAYMENT_REQUIRED)

    
    @action(detail=True, methods=['delete'])
    def remove(self, request : HttpRequest, pk=None):
        if not request.user.is_superuser:
            return Response({
                "message":"You do not have the priviledge to remove this"
            }, status= status.HTTP_401_UNAUTHORIZED)
        booking = get_object_or_404(Booking, pk=pk)
        booking.delete()
        return Response({
            'message': "Deleted successfully" 
        }, status = status.HTTP_204_NO_CONTENT)

        
class VehicleScheduleViewSet(viewsets.ModelViewSet):
    queryset = VehicleSchedule.objects.all()
    serializer_class = VehicleScheduleSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        vehicle_id = self.request.query_params.get('vehicle_id')
        if vehicle_id:
            vehicle = Vehicle.objects.filter(id=vehicle_id).first()
            if vehicle:
                three_months_from_now = timezone.now() + timedelta(days=150)
                return VehicleSchedule.objects.filter(vehicle=vehicle, travel_datetime__lte=three_months_from_now)
        return VehicleSchedule.objects.none()

    @action(detail=True, methods=['get'])
    def available_seats(self, request, pk=None):
        schedule = self.get_object()
        return Response({'available_seats': schedule.available_seats()})

class PaymentViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer

    @action(detail=True, methods=['post'])
    def complete_payment(self, request, pk=None):
        payment = get_object_or_404(Payment, pk=pk)
        payment_status = verify_payment(payment)
        
        if payment_status == 'COMPLETED':
            payment.status = 'COMPLETED'
            booking = payment.booking
            booking.status = 'CONFIRMED'
            booking.confirmed = True
            booking.schedule.booked_seats.extend(booking.booked_seats)
            booking.schedule.save()
            booking.save()
        else:
            payment.status = 'FAILED'

        payment.save()
        return Response(PaymentSerializer(payment).data)
    
class GuestBookingViewSet(viewsets.ModelViewSet):
    queryset = GuestBooking.objects.all()
    serializer_class = GuestBookingSerializer
    permission_classes = []

    @action(detail=True, methods=['post'])
    def book_seat(self, request, pk=None):
        schedule = get_object_or_404(VehicleSchedule, pk=pk)
        seats = request.data.get('seats', [])
        guest_data = request.data

        adult_count = guest_data.get('number_of_adults', 1)
        children_count = guest_data.get('number_of_children_below_10', 0)
        passenger_count = passengerCount(adult_count, children_count)

        if passenger_count > len(seats):
            return Response(
                {'error': 'Passenger boarding this vehicle is more than the seats booked'},
                status=status.HTTP_406_NOT_ACCEPTABLE
            )

        # Check seat availability
        available_seats = schedule.available_seats()
        if not all(seat in available_seats for seat in seats):
            return Response({'error': 'One or more seats are already booked'}, status=status.HTTP_410_GONE)

        trip_type = guest_data.get('trip_type', 'ONE WAY')
        amount_to_pay = schedule.vehicle.price * len(seats) if trip_type == "ONE WAY" else 2 * schedule.vehicle.price * len(seats)

        # Create GuestBooking
        guest_booking = GuestBooking.objects.create(
            full_name=f"{guest_data.get('title', '')} {guest_data.get('surname', '')} {guest_data.get('firstname', '')}",
            email=guest_data.get('email'),
            phone_number=guest_data.get('phone'),
            nok_full_name=f"{guest_data.get('nok-title', '')} {guest_data.get('nok-surname', '')}",
            nok_phone_number=guest_data.get('nok-phone'),
            vehicle=schedule.vehicle,
            trip_type=trip_type,
            status='PENDING',
            pickup_state=schedule.pickup_state,
            destination_state=schedule.destination_state,
            number_of_seats=len(seats),
            number_of_adults=adult_count,
            number_of_children_below_10=children_count,
            total_cost=amount_to_pay,
            travel_date=schedule.travel_datetime,
            schedule=schedule,
            booked_seats=seats
        )

        # Redirect to payment gateway
        payment_detail = initiate_payment(guest_booking.booking_code, guest_booking.total_cost, guest_booking.email)
        if payment_detail['success']:
            payment_url = payment_detail['payment_url']
            access_code = payment_detail['access_code']
            return Response({
                'payment_url': payment_url,
                'booking_code': guest_booking.booking_code,
                'access_code': access_code,
                'total_amount': guest_booking.total_cost
            }, status=status.HTTP_201_CREATED)
        else:
            guest_booking.delete()
            return Response({
                'message': payment_detail['error']
            }, status=status.HTTP_402_PAYMENT_REQUIRED)

class GuestPaymentViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = GuestPaymentSerializer

    @action(detail=True, methods=['post'])
    def complete_payment(self, request, pk=None):
        payment = get_object_or_404(GuestPayment, pk=pk)
        payment_status = verify_payment(payment)
        
        if payment_status == 'COMPLETED':
            payment.status = 'COMPLETED'
            booking = payment.booking
            booking.status = 'CONFIRMED'
            booking.confirmed = True
            booking.schedule.booked_seats.extend(booking.booked_seats)
            booking.schedule.save()
            booking.save()
        else:
            payment.status = 'FAILED'

        payment.save()
        return Response(GuestPaymentSerializer(payment).data)
 