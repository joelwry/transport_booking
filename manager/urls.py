from django.urls import path
from manager import views


app_name = "manager"

urlpatterns = [
    path("index/", views.manageIndexView, name='managerIndex'),

    # add new company
    path("add-company/", views.AddCompany, name='newcompany'),

    # add new vehicle
    path("add-vehicle/", views.AddVehicle, name='newvehicle'),
]





