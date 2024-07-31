from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from booking.models import TransportationCompany, State, Terminals, Vehicle, Traveller, Message, Booking, Payment
from .serializers import (
    TransportationCompanySerializer, StateSerializer, TerminalsSerializer, VehicleSerializer,
    TravellerSerializer, MessageSerializer, BookingSerializer, PaymentSerializer
)

@api_view(['GET', 'POST'])
def transportation_company_list(request):
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
def transportation_company_detail(request, pk):
    try:
        company = TransportationCompany.objects.get(pk=pk)
    except TransportationCompany.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = TransportationCompanySerializer(company)
        return Response(serializer.data)
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

class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer