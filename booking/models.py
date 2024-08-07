from typing import Iterable
from django.db import models
from django.contrib.auth.models import User
from .utils.generators import generateBookingId
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from datetime import timedelta
from django.utils import timezone
from datetime import datetime 
from django.utils.text import slugify
from .utils.unique_slug import generate_unique_slug


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
    image = models.ImageField(upload_to="static/image/company", null=True, default='None')
    # added slug field and will be aadded to other model as well to make urls user and SEO friendly 
    slug = models.SlugField(unique=True, )

    def __str__(self):
        return self.name
    # Altered the save function to add slug to model object for a nice url
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = generate_unique_slug(self, slugify(self.name))
        super(TransportationCompany, self).save(*args, **kwargs)




class State(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Terminals(models.Model):
    state = models.ForeignKey(to=State, on_delete=models.CASCADE)
    area = models.CharField(max_length = 50)
    address = models.CharField(max_length=255)

    def __str__(self):
        return f'{self.area} <=> {self.state}'

class Vehicle(models.Model):
    plate_number = models.CharField(max_length=200)
    capacity = models.PositiveIntegerField(default=1)
    terminal1 = models.ForeignKey(Terminals, default=None, blank=True, related_name='address1',on_delete=models.SET_NULL, null=True) # Their address in state 1
    terminal2= models.ForeignKey(to= Terminals, default=None, blank=True, related_name='address2',on_delete=models.SET_NULL, null=True) # Their address in state 2
    available = models.BooleanField(default=True)
    company= models.ForeignKey(to=TransportationCompany,on_delete=models.CASCADE)
    price = models.DecimalField(decimal_places=3, max_digits=10, default=15000.000)
    def __str__(self):
        return f' vehicle {self.plate_number} => {self.company.name}'

class Traveller(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    phone = models.CharField(max_length=15, default='None')
    state = models.CharField(max_length=30, default='None')
    gender = models.CharField(max_length=1, choices=(("M","MALE"),("F","FEMALE"),("U","UNSPECIFIED")),default="U")

    def __str__(self):
        return self.user.email if self.user.email else self.user.username 



class VehicleSchedule(models.Model):
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE)
    pickup_state = models.ForeignKey(State, on_delete=models.CASCADE, related_name='schedule_pickup_state')
    destination_state = models.ForeignKey(State, on_delete=models.CASCADE, related_name='schedule_destination_state')
    travel_datetime = models.DateTimeField()
    number_of_bookings = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"Schedule for {self.vehicle} from {self.pickup_state} to {self.destination_state} on {self.travel_datetime}"

    def is_past_due(self):
        return datetime.now() > self.travel_datetime

    def clean(self):
        if self.travel_datetime <= timezone.now():
            raise ValidationError('Travel date must be in the future.')


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
    TRIP_TYPE = [
        ("ONE WAY", "one way ticket"),
        ("TWO WAY", "two way ticket")
    ]
    customer = models.ForeignKey(Traveller, on_delete=models.CASCADE)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE)
    trip_type = models.CharField(max_length=25,  choices=TRIP_TYPE, default=TRIP_TYPE[0][0])
    booking_code = models.CharField(max_length=25, unique=True, default=generateBookingId)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    pickup_state = models.ForeignKey(State, on_delete=models.SET_NULL, null=True, related_name='pickup_state',blank=True)
    destination_state = models.ForeignKey(State, on_delete=models.SET_NULL, null=True, related_name='destination_state',)
    number_of_seats = models.PositiveIntegerField(default=1)
    number_of_children_below_10 = models.PositiveIntegerField(default=0)
    number_of_adults = models.PositiveIntegerField(default=1)
    total_cost = models.DecimalField(max_digits=10, decimal_places=2)
    travel_date = models.DateTimeField(default = default_travel_date)
    return_date = models.DateTimeField(null=True, blank=True)
    booking_date = models.DateTimeField(auto_now_add=True)
    confirmed = models.BooleanField(default=False)
    payment_id = models.CharField(max_length=100, null=True, blank=True)
    ticket_sent = models.BooleanField(default=False)

    def __str__(self):
        return f"Booking {self.booking_code} by {self.customer.user.username}"

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

