from django.shortcuts import render, redirect
from booking.models import Vehicle, TransportationCompany, Booking, Terminals, Traveller
from django.contrib.auth import login, authenticate
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.csrf import csrf_protect
from django.http import JsonResponse,HttpRequest

from django.utils import timezone
from django.db.models import Count


# Create your views here.

@csrf_protect
def managerLogin(request:HttpRequest):    
    if request.user.is_authenticated:
        if request.user.is_staff:
            return redirect('manager:managerIndex')
        else:
            return redirect('user_dashboard')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password = password)

        if user is not None:
            if user.is_staff:
                login(request, user)
                return JsonResponse({'success': True, 'redirect_url': '/manager/index'})
            else:
                return JsonResponse({'success':False, 'message':'you dont have permission to this page'})
        else:
            return JsonResponse({'success' : False, 'message': 'invalid username or password'})


    return render(request, 'manager/manager-login.html')


import random
# manager index view
@staff_member_required(login_url='manager:managerlogin')
def manageIndexView(request):
    traveller = Traveller.objects.all().count()
    companies = TransportationCompany.objects.all().count()
    bookings_pending = Booking.objects.filter( status="PENDING").count()
    print(bookings_pending)

# Get today's date
    today = timezone.now().date()
    
    # Get the start of the week (Monday)
    start_of_week = today - timezone.timedelta(days=today.weekday())
    
    # Get bookings per day for the current week
    bookings_per_day = Booking.objects.filter(booking_date__date__gte=start_of_week) \
                                      .values('booking_date__date') \
                                      .annotate(count=Count('id')) \
                                      .order_by('booking_date__date')
    
    # Create a dictionary to hold the counts for each day of the week
    days_of_week = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    bookings_dict = {day: 0 for day in days_of_week}
    
    for booking in bookings_per_day:
        day_of_week = booking['booking_date__date'].strftime('%A')
        bookings_dict[day_of_week] = booking['count']

    context = {
       
        'num_traveller' : traveller,
        'num_companies' : companies,
        'num_pending_booking': bookings_pending,
        'days_of_week': list(bookings_dict.keys()),
        'bookings_per_day': list(bookings_dict.values()),
    }
    return render(request, "manager/index.html", context)# manager index view

# add new company
@staff_member_required(login_url='manager:managerlogin')
def AddCompany(request):
    if request.method == 'POST':
        company_name = request.POST.get('company_name')
        company_email = request.POST.get('company_email')
        company_phone = request.POST.get('company_phone')
        company_address = request.POST.get('company_address')
        company_info = request.POST.get('company_info')
        company_logo = request.POST.get('company_logo')

        if not (company_name | company_email | company_phone | company_address | company_logo):
            return JsonResponse({'success' : False, 'message' : 'filled with * are required'})

    return render(request, "manager/add_company.html")# manager index view


# add new vehicle to lish
@staff_member_required(login_url='manager:managerlogin')
def AddVehicle(request):
    return render(request, "manager/add_vehicle.html")





def booking_stats(request):
    # Get today's date
    today = timezone.now().date()
    
    # Get the start of the week (Monday)
    start_of_week = today - timezone.timedelta(days=today.weekday())
    
    # Get the start of the month
    start_of_month = today.replace(day=1)
    
    # Fetch weekly booking data
    weekly_bookings = Booking.objects.filter(booking_date__gte=start_of_week) \
                                     .values('status') \
                                     .annotate(count=Count('id'))
    
    # Fetch monthly booking data
    monthly_bookings = Booking.objects.filter(booking_date__gte=start_of_month) \
                                      .values('status') \
                                      .annotate(count=Count('id'))
    
    context = {
        'weekly_bookings': list(weekly_bookings),
        'monthly_bookings': list(monthly_bookings),
    }
    
    return JsonResponse(monthly_bookings, safe=False)
