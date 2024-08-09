from rest_framework import serializers
from booking.models import Booking, Traveller, TransportationCompany, Vehicle,  State, Payment, Message,Terminals, VehicleSchedule

class TransportationCompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = TransportationCompany
        fields = '__all__'

class VehicleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vehicle
        fields = '__all__'

class StateSerializer(serializers.ModelSerializer):
    class Meta:
        model = State
        fields = '__all__'

class VehicleRouteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vehicle
        fields = '__all__'

class TravellerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Traveller
        fields = '__all__'

class BookingSerializer(serializers.ModelSerializer):
    pickup_state_name = serializers.SerializerMethodField()
    destination_state_name = serializers.SerializerMethodField()

    class Meta:
        model = Booking
        #fields = '__all__'
        fields = [
            'id', 'customer', 'vehicle', 'trip_type', 'booking_code', 'status',
            'pickup_state', 'destination_state', 'number_of_seats', 'number_of_children_below_10',
            'number_of_adults', 'total_cost', 'travel_date', 'return_date', 'booking_date', 
            'confirmed', 'payment_id', 'ticket_sent', 'schedule', 'booked_seats','pickup_state_name',"destination_state_name"
        ]
    
    def get_pickup_state_name(self, obj):
        return obj.pickup_state.name

    def get_destination_state_name(self, obj):
        return obj.destination_state.name 

class MessageSerializer(serializers.ModelSerializer):
    class Meta :
        model = Message
        fields = '__all__'

class TerminalsSerializer:
    class Meta:
        model = Terminals
        fields = "__all__"

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = '__all__'


class VehicleScheduleSerializer(serializers.ModelSerializer):
    available_seats = serializers.SerializerMethodField()
    vehicle_capacity = serializers.SerializerMethodField()
    vehicle_price = serializers.SerializerMethodField()
    vehicle_company = serializers.SerializerMethodField()
    pickup_state_name = serializers.SerializerMethodField()
    destination_state_name = serializers.SerializerMethodField()
    class Meta:
        model = VehicleSchedule
        fields = ['id', 'vehicle', 'pickup_state', 'destination_state', 'travel_datetime', 'number_of_bookings', 'booked_seats', 'available_seats', 'vehicle_capacity', 'vehicle_price','vehicle_company','pickup_state_name','destination_state_name']

    def get_available_seats(self, obj):
        return obj.available_seats()

    def get_vehicle_capacity(self, obj):
        return obj.vehicle.capacity

    def get_vehicle_price(self, obj):
        return obj.vehicle.price

    def get_vehicle_company(self, obj):
        return obj.vehicle.company.name  

    def get_pickup_state_name(self, obj):
        return obj.pickup_state.name

    def get_destination_state_name(self, obj):
        return obj.destination_state.name 