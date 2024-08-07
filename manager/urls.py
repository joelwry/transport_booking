from django.urls import path
from manager import views



app_name = "manager"

urlpatterns = [

    # manager login page
    path("",  views.managerLogin, name="managerlogin"),

    # manager index page
    path("index/", views.manageIndexView, name='managerIndex'),

    # add new company
    path("add-company/", views.AddCompany, name='newcompany'),

    # company details view
    path("company-detail/<int:company_id>/<slug:slug>", views.companyDetail, name="company-detail"),
    
    # company delete view
    path("deletecompany/<int:company_id>/", views.deleteCompany, name="detelecompany"),

    # add new vehicle
    path("add-vehicle/", views.AddVehicle, name='newvehicle'),
     
    # add new vehicle
    path("companies/", views.companyList, name='companies'),

    path("bookings/", views.BookingListView.as_view(), name="bookings"),

    # # show analytics
    # path("analytics/", views.booking_stats, name="analytics"),

    path("company-analytics/", views.company_analytics, name="cma")
]





