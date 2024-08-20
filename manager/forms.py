from django import forms
from django.core import exceptions
from booking.models import Vehicle, TransportationCompany, Terminals, State, VehicleSchedule






class addNewCompanyForm(forms.ModelForm):
   class Meta:
      model = TransportationCompany
      fields = ['image', 'name', 'address', 'about', 'email', 'phone_number', ]

class addNewVehicle(forms.ModelForm):
   class Meta:
      model = Vehicle
      fields = ['plate_number', 'terminal1', 'terminal2', 'company', 'capacity', 'price']

class addTerminal(forms.ModelForm):
   class Meta:
      model = Terminals
      fields = ['state', 'area', 'address']

class addState(forms.ModelForm):
   class Meta:
      model = State
      fields = '__all__'
     
class CreateSchedule(forms.ModelForm):
   class Meta:
      fields = '__all__'