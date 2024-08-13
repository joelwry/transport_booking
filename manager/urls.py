from django.urls import path
from manager import views



app_name = "manager"

urlpatterns = [

    # manager login page
    path("",  views.managerLogin, name="managerlogin"),

    # manager index page
    path("index/", views.manageIndexView, name='managerIndex'),


    #COMPANY VIEW

    # list company view
    path("companies/", views.companyList, name='companies'),

    # add new company
    path("add-company/", views.addNewCompany, name='newcompany'),

    # company details view
    path("company-detail/<int:company_id>/<slug:slug>", views.companyDetail, name="company-detail"),
    
    # company delete view
    path("deletecompany/<int:company_id>", views.deleteCompany, name="detelecompany"),


    # VEHICLE VIEW

    # add new vehicle
    path("add-vehicle/<int:id>/<slug:slug>/", views.AddVehicle, name='newvehicle'),

    # Delete vehicle
    path("delete-vehicle/<int:id>/", views.DeleteVehicle, name='deletevehicle'),


    # STATE VIEW
    path("state-list/",views.StateView, name="states"),

    # state detail view
    path("state-detail/<int:statecode>",views.StateDetailView, name="states-detail"),



    # TERMINAL VIEWS

    # add terminal view page
    path("add-new-terminal/", views.addTerminaLView, name='add-terminal-view'),

    # add terminal actions view
    path("add-terminal-action/", views.AddNewTerminal, name='add-terminal-action'),

    # create terminal
    path('create-terminal/', views.CreateTerminal, name = 'create-terminal'),



    path("bookings/", views.BookingListView.as_view(), name="bookings"),
    path("bookings-detail/<str:bookcode>/", views.bookingDetailView, name="booking-detail"),

    # # show analytics
    # path("analytics/", views.booking_stats, name="analytics"),

    path("company-analytics/", views.company_analytics, name="cma")
]





