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
from .utils.payment_gateway import initiate_payment, verify_payment
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
        try:
            payment_detail = initiate_payment(booking.booking_code,booking.total_cost, request.user.email)
            if payment_detail['success']:
                payment_url = payment_detail['payment_url']
                access_code = payment_detail['access_code']
                access_code_modified = payment_detail['access_modified']
                return Response({
                    'external_payment_url': payment_url,
                    'booking_code': booking.booking_code,
                    'access_code' : access_code,
                    'total_amount': booking.total_cost,
                    'access_code_modified': access_code_modified,
                    'internal_payment_url':f'/payment/{booking.booking_code}/{access_code}/{payment_detail['amount']}/'
                }, status=status.HTTP_201_CREATED) 
        except Exception as e :
            booking.delete()
            return Response({
                'message': 'Unable to serve a connection to our payment gateway.. ensure you have an internet connection other retry booking'
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


@csrf_exempt
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def verifyPaymentView(request, reference):
    user = request.user

    # Verify the payment with Paystack
    payment_verification = verify_payment(reference)
    
    if not payment_verification['status']:
        return Response({'status': False, 'message': payment_verification['error']}, status=400)

    booking_code = payment_verification['reference']
    try:
        booking = Booking.objects.get(booking_code=booking_code, customer__user=user)
        
        if booking.status != 'PENDING':
            return Response({'status': False, 'message': 'Booking is not pending.'}, status=400)
        
        # Additional validations (e.g., amount check)
        required_payment = booking.total_cost * 100
        payment_made = payment_verification['amount']
        if required_payment < payment_made :
            return Response({'status': False, 'message': f'Incorrect payment amount.. A payment of NGN{booking.total_cost} was required but a payment of {payment_made/100} was made which is NGN{(payment_made/100) - booking.total_cost} less than the specified amount'}, status=400)
        
        # Update booking status and reserved seats
        booking.status = 'CONFIRMED'
        booking.payment_id = payment_verification['id']
        booking.confirmed = True
        booking.save()

        payment = Payment.objects.filter(booking = booking).first()
        if payment == None :
            Payment.objects.create(booking=booking, amount= booking.total_cost,status='COMPLETED')
        elif payment.status != 'COMPLETED':
            payment.status = 'COMPLETED'
            payment.amount = booking.total_cost
            payment.save()

        # Update VehicleSchedule for reserved seats
        schedule = booking.schedule
        seats = booking.booked_seats
        schedule.booked_seats.extend(seats)
        # still need validation for seat if already booked by someone else etc
        # for seat in booking.booked_seats:
        #     schedule.reserve_seat(seat)
        schedule.save()


        return Response({'status': True, 'message': 'Payment verified and booking confirmed', 'vehicle_schedule':schedule.id, 'booking':"booking.id"})
    
    except Booking.DoesNotExist:
        return Response({'status': False, 'message': 'Booking does not exist or does not belong to the user.'}, status=404)


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
    permission_classes = [AllowAny]

    @action(detail=True, methods=['post'])
    def book_seat(self, request, pk=None):
        schedule = get_object_or_404(VehicleSchedule, pk=pk)
        schedule = VehicleSchedule.objects.filter(pk=pk).first()
        if not schedule :
            return Response(
                {'message': 'The Vehicle schedule specified does not exist ..','error':True},
                status=status.HTTP_404_NOT_FOUND
            )
        seats = request.data.get('seats', [])
        print(type(seats))
        print(seats)
        guest_data = request.data

        adult_count = guest_data.get('number_of_adults', 1)
        children_count = guest_data.get('number_of_children_below_10', 0)
        passenger_count = passengerCount(adult_count, children_count)

        if passenger_count > len(seats):
            return Response(
                {'message': 'Passenger boarding this vehicle is more than the seats booked','error':True},
                status=status.HTTP_406_NOT_ACCEPTABLE
            )

        # Check seat availability
        available_seats = schedule.available_seats()
        if not all(seat in available_seats for seat in seats):
            return Response({'message': 'One or more seats are already booked','error':True}, status=status.HTTP_410_GONE)

        trip_type = guest_data.get('trip_type', 'ONE WAY')
        amount_to_pay = schedule.vehicle.price * len(seats) if trip_type == "ONE WAY" else 2 * schedule.vehicle.price * len(seats)

        # Create GuestBooking
        try :
            guest_booking = GuestBooking(
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
                guest_booking.save()
                payment_url = payment_detail['payment_url']
                access_code = payment_detail['access_code']
                return Response({
                    "error":False,
                    'payment_url': payment_url,
                    'booking_code': guest_booking.booking_code,
                    'access_code': access_code,
                    'total_amount': guest_booking.total_cost
                }, status=status.HTTP_201_CREATED)
            else:
                return Response({
                    'error':True,
                    'message': payment_detail['error']
                }, status=status.HTTP_402_PAYMENT_REQUIRED)
            
        except Exception as e :
            return Response({
                'message': 'Seems like you do not have not established a connection to our payment host.. Do ensure you have a stable internet connection! ',
                'error': True
            }, status= status.HTTP_408_REQUEST_TIMEOUT)

@csrf_exempt
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def verifyPaymentView(request, reference):
    user = request.user

    # Verify the payment with Paystack
    payment_verification = verify_payment(reference)
    
    if not payment_verification['status']:
        return Response({'status': False, 'message': payment_verification['error']}, status=400)

    booking_code = payment_verification['reference']
    try:
        booking = Booking.objects.get(booking_code=booking_code, customer__user=user)
        
        if booking.status != 'PENDING':
            return Response({'status': False, 'message': 'Booking is not pending.'}, status=400)
        
        # Additional validations (e.g., amount check)
        required_payment = booking.total_cost * 100
        payment_made = payment_verification['amount']
        if required_payment < payment_made :
            return Response({'status': False, 'message': f'Incorrect payment amount.. A payment of NGN{booking.total_cost} was required but a payment of {payment_made/100} was made which is NGN{(payment_made/100) - booking.total_cost} less than the specified amount'}, status=400)
        
        # Update booking status and reserved seats
        booking.status = 'CONFIRMED'
        booking.payment_id = payment_verification['id']
        booking.confirmed = True
        booking.save()

        payment = Payment.objects.filter(booking = booking).first()
        if payment == None :
            Payment.objects.create(booking=booking, amount= booking.total_cost,status='COMPLETED')
        elif payment.status != 'COMPLETED':
            payment.status = 'COMPLETED'
            payment.amount = booking.total_cost
            payment.save()

        # Update VehicleSchedule for reserved seats
        schedule = booking.schedule
        seats = booking.booked_seats
        schedule.booked_seats.extend(seats)
        # still need validation for seat if already booked by someone else etc
        # for seat in booking.booked_seats:
        #     schedule.reserve_seat(seat)
        schedule.save()


        return Response({'status': True, 'message': 'Payment verified and booking confirmed', 'vehicle_schedule':schedule.id, 'booking':"booking.id"})
    
    except Booking.DoesNotExist:
        return Response({'status': False, 'message': 'Booking does not exist or does not belong to the user.'}, status=404)

@csrf_exempt
@api_view(['GET'])
@permission_classes([AllowAny])
def verifyGuestPaymentView(request, reference):
    phone_number = request.GET['phone_number']
    email = request.GET['email']

    # Verify the payment with Paystack
    payment_verification = verify_payment(reference)
    
    if not payment_verification['status']:
        return Response({'status': False, 'message': payment_verification['error']}, status=400)

    booking_code = payment_verification['reference']
    try:
        booking = GuestBooking.objects.get(booking_code=booking_code, email = email, phone_number = phone_number)
        
        if booking.status != 'PENDING':
            return Response({'status': False, 'message': 'Booking is not pending.'}, status=400)
        
        # Additional validations (e.g., amount check)
        required_payment = booking.total_cost * 100
        payment_made = payment_verification['amount']
        if required_payment < payment_made :
            return Response({'status': False, 'message': f'Incorrect payment amount.. A payment of NGN{booking.total_cost} was required but a payment of {payment_made/100} was made which is NGN{(payment_made/100) - booking.total_cost} less than the specified amount'}, status=400)
        
        # Update booking status and reserved seats
        booking.status = 'CONFIRMED'
        booking.payment_id = payment_verification['id']
        booking.confirmed = True
        booking.save()

        payment = Payment.objects.filter(booking = booking).first()
        if payment == None :
            GuestPayment.objects.create(booking=booking, amount= booking.total_cost,status='COMPLETED')
        elif payment.status != 'COMPLETED':
            payment.status = 'COMPLETED'
            payment.amount = booking.total_cost
            payment.save()

        # Update VehicleSchedule for reserved seats
        schedule = booking.schedule
        seats = booking.booked_seats
        schedule.booked_seats.extend(seats)
        # still need validation for seat if already booked by someone else etc
        # for seat in booking.booked_seats:
        #     schedule.reserve_seat(seat)
        schedule.save()


        return Response({'status': True, 'message': 'Payment verified and booking confirmed', 'vehicle_schedule':schedule.id, 'booking':"booking.id"})
    
    except GuestBooking.DoesNotExist:
        return Response({'status': False, 'message': 'Booking does not exist or does not belong to the user.'}, status=404)

