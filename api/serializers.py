from rest_framework import serializers
from booking.models import Booking, Traveller, TransportationCompany, Vehicle,  State, Payment, Message,Terminals

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
    class Meta:
        model = Booking
        fields = '__all__'

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
