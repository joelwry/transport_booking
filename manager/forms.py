from django import forms
from django.core import exceptions
from booking.models import Vehicle








class addNewVehicle(forms.ModelForm):
#    plate_number = forms.CharField( max_length=20, required=True)
#    terminal1 = forms.CharField( max_length=30, required=True)
#    terminal2 = forms.CharField( max_length=30, required=True)
#    company = forms.CharField( max_length=35, required=True)
#    capacity = forms.CharField( max_length=4, required=True)
#    price = forms.CharField( max_length=6, required=True)

   class Meta:
      model = Vehicle
      fields = ['plate_number', 'terminal1', 'terminal2', 'company', 'capacity', 'price']


     