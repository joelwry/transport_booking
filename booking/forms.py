from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from .models import Traveller, Booking,TransportationCompany,State
import re

# to be removed in place of SignupForm
class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email',"first_name", "last_name",'password1', 'password2']

class TravellerForm(forms.ModelForm):
    class Meta:
        model = Traveller
        fields = ['phone', 'state', 'gender']

class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = [ 'number_of_seats', 'travel_date']

class SignUpForm(forms.ModelForm):
    password1 = forms.CharField(widget=forms.PasswordInput, label="Password")
    password2 = forms.CharField(widget=forms.PasswordInput, label="Confirm Password")

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def clean_password1(self):
        password = self.cleaned_data.get('password1')
        if len(password) < 8:
            raise ValidationError("Password must be at least 8 characters long.")
        if not re.search(r'[A-Z]', password):
            raise ValidationError("Password must contain at least one uppercase letter.")
        if not re.search(r'[a-z]', password):
            raise ValidationError("Password must contain at least one lowercase letter.")
        if not re.search(r'\d', password):
            raise ValidationError("Password must contain at least one digit.")
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            raise ValidationError("Password must contain at least one special character.")
        return password

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        if not password1 or not password2 or password1 != password2:
            raise ValidationError("Passwords do not match.")
        return cleaned_data

class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)

class AdvancedSearchForm(forms.Form):
    start_state = forms.CharField(required=False,label='Start state')
    destination_state = forms.CharField(required=False,label='Destination state')
    min_price = forms.DecimalField(required=False, label="Min Price", decimal_places=3, max_digits=10)
    max_price = forms.DecimalField(required=False, label="Max Price", decimal_places=3, max_digits=10)
    available = forms.BooleanField(required=False, label="Only Show Available")
    company = forms.CharField(required=False,label='Company')
    #company = forms.ModelChoiceField(queryset=TransportationCompany.objects.all(), required=False, label="Company")