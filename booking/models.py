from typing import Iterable
from django.db import models
from django.contrib.auth.models import User
from .utils.generators import generateBookingId
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from datetime import timedelta
from django.utils import timezone

MESSAGE_TYPE = [
    ("Enquiry","ENQUIRE"),("Complain","COMPLAIN"),("Request","REQUEST")
]

def default_travel_date():
        return timezone.now() + timedelta(days=7)


class TransportationCompany(models.Model):
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=500) #headquarter
    about = models.TextField(null=True)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(
        max_length=15,
        null=True,
        validators=[
            RegexValidator(
                regex='^\d+$',
                message='Phone number must contain only digits',
                code='invalid_phone_number'
            )
        ]
    )

    def __str__(self):
        return self.name

class State(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name
    
class Vehicle(models.Model):
    plate_number = models.CharField(max_length=200)
    capacity = models.PositiveIntegerField(default=1)
    terminal1 = models.CharField(max_length=255, default=None, blank=True) # Their address in state 1
    terminal2= models.CharField(max_length=255, default=None, blank=True) # Their address in state 2
    available = models.BooleanField(default=True)
    company= models.ForeignKey(to=TransportationCompany,on_delete=models.CASCADE)

    def __str__(self):
        return f' vehicle {self.plate_number} => {self.company.name}'


class VehicleRoute(models.Model):
    vehicle = models.OneToOneField(Vehicle, on_delete=models.CASCADE)
    state1 = models.ForeignKey(to=State, on_delete=models.CASCADE, related_name='state1_travelled_to')
    state2 = models.ForeignKey(to=State, on_delete=models.CASCADE, related_name='state2_travelled_to')
    price = models.DecimalField(decimal_places=3, max_digits=10, default=100.000)

    def __str__(self):
        return f'Route for {self.vehicle} with price {self.price}'

class Traveller(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    phone = models.CharField(max_length=15, default='None')
    state = models.CharField(max_length=30, default='None')
    gender = models.CharField(max_length=1, choices=(("M","MALE"),("F","FEMALE"),("U","UNSPECIFIED")),default="U")


class Message(models.Model):
    type = models.CharField(max_length=20, choices=MESSAGE_TYPE)
    sender = models.ForeignKey(Traveller,on_delete=models.CASCADE)
    message = models.TextField()
    delivered = models.BooleanField(default=False)
    # i want this part to only be inserted by admin either a staff or super admin...is there any way to achieve this functionality
    admin_reply = models.TextField()
    

class Booking(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('CONFIRMED', 'Confirmed'),
        ('CANCELLED', 'Cancelled'),
    ]
    customer = models.ForeignKey(Traveller, on_delete=models.CASCADE)
    route = models.ForeignKey(VehicleRoute, on_delete=models.CASCADE)
    booking_code = models.CharField(max_length=25, unique=True, default=generateBookingId)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    number_of_seats = models.PositiveIntegerField(default=1)
    total_cost = models.DecimalField(max_digits=10, decimal_places=2)
    travel_date = models.DateTimeField(default = default_travel_date)
    booking_date = models.DateTimeField(auto_now_add=True)
    confirmed = models.BooleanField(default=False)
    payment_id = models.CharField(max_length=100, null=True, blank=True)
    ticket_sent = models.BooleanField(default=False)

    def __str__(self):
        return f"Booking {self.booking_code} by {self.user.username}"

class Payment(models.Model):
    PAYMENT_STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
    ]
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=10, choices=PAYMENT_STATUS_CHOICES, default='PENDING')
    payment_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment for {self.booking.booking_code}"


class Staff(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_super_admin = models.BooleanField(default=False)

# we will be using this model to track user attempt to login 
class LoginAttempt(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    attempts = models.IntegerField(default=0)
    locked_until = models.DateTimeField(null=True, blank=True)
