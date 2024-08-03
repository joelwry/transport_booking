from django.shortcuts import render
from booking.models import Vehicle, TransportationCompany, Booking, Terminals, Traveller


# Create your views here.

# manager index view
def manageIndexView(request):
    return render(request, "manager/index.html")# manager index view

# add new company
def AddCompany(request):
    return render(request, "manager/add_company.html")# manager index view

# add new vehicle to lish
def AddVehicle(request):
    return render(request, "manager/add_vehicle.html")
