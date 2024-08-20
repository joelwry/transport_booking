from django.shortcuts import render, redirect, get_object_or_404
from booking.models import Vehicle, TransportationCompany, Booking, Terminals, Traveller, State
from django.contrib.auth import login, authenticate
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.http import require_POST
from django.views.generic import ListView, DetailView
from django.views.decorators.csrf import csrf_protect
from django.http import JsonResponse,HttpRequest, HttpResponse

from django.utils import timezone
from django.db.models import Count,Q

from .forms import addNewVehicle, addNewCompanyForm, addTerminal, addState, CreateSchedule


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
@csrf_protect
def addNewCompany(request):
    if request.method == 'POST':
        form = addNewCompanyForm(request.POST, request.FILES)
        if form.is_valid():
            company = form.save(commit=False)
            name = request.POST.get('name')
            name = name.upper()
            checker = TransportationCompany.objects.filter(name = name).first()
            if checker:
                return JsonResponse({'success':False, 'message': 'Transportation Company already exist'}, status = 400)
            else:
                company.save()
                return JsonResponse({'success':True, 'message': 'Company added successfully'}, status = 200)
        else:
           errors = form.errors.as_json(escape_html=True)
           return JsonResponse({'success': False, 'message': errors }, status = 400)
    else:
        form = addNewCompanyForm()
    return render(request, "manager/add_company.html")



# company list
@staff_member_required
def companyList(request):
    companies = TransportationCompany.objects.all()
    return render(request,'manager/company_list.html', {'companies':companies})




@staff_member_required
@require_POST
def deleteCompany(request, company_id):
    company = TransportationCompany.objects.filter(pk = company_id).first()
    try:
        company.delete()
    except Exception as e:
        return JsonResponse({'success':False, 'message' : 'An error occured object can\'t be deleted'})
    return JsonResponse({'success': True, 'message': 'company deleted successfully'})




@staff_member_required
def companyDetail(request, company_id ):
    terminalsall = Terminals.objects.all()
    company = get_object_or_404(TransportationCompany, id = company_id)
    return render(request, 'manager/companydetail.html', {'company': company, 'terminals':terminalsall})

def company_analytics(request):
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


# ADD NEW VEHICLE
@require_POST
def AddVehicle(request, id ):
    if request.user.is_staff:
        company = get_object_or_404(TransportationCompany, pk = id)   
        form = addNewVehicle(request.POST)
        if form.is_valid:
            vehicle_form = form.save(commit=False)
            plate_number = request.POST.get('plate_number')
            checker = Vehicle.objects.filter(plate_number = plate_number).first()
            if checker:
                return JsonResponse({'success' : False, 'message' : 'vehicle with plate number already Exist!'}, status = 400)
            vehicle_form.save()
            return JsonResponse({'success' : True, 'message' : 'Vehicle Added successfully'}, status = 200)
        else:
            # else return error message
            return JsonResponse({'success' : False, 'message' : vehicle_form.errors }, status = 400)
    return JsonResponse({'success' : False, 'message' : 'An error Occured'}, status = 400)

# DELETE VEHICLE
@require_POST
@csrf_protect
def DeleteVehicle(request, id):
    if request.user.is_staff:
        VehicleItem = Vehicle.objects.get(id = id)
        if VehicleItem:
            VehicleItem.delete()
            return JsonResponse({'success' : True, 'message': 'Vehicle deleted successfully'}, status = 200)
        return JsonResponse({'success' : False, 'message' : 'Error Deleting Vehicle'}, status = 404)
    return JsonResponse({'success': False, 'message':'An Error Occured'}, status = 400)


# ADD TERMINAL ACTION VIEW
@staff_member_required(login_url='manager:managerlogin')
@require_POST
def AddNewTerminal(request):
    if request.user.is_staff:
        state = request.POST.get('state')
        area = request.POST.get('area')
        address = request.POST.get('address') 
        state = State.objects.get(id = state)
        try:
            creator = Terminals.objects.create(state = state, area = area, address = address)
        except Exception as e:
            
            return JsonResponse({'success' : False, 'message': 'Error Saving Terminal'}, status = 400)
        if creator:
            return JsonResponse({'success' : True, 'message': 'Terminal Added Success'}, status = 200)
        return JsonResponse({'success' : False, 'message': 'An error occured try Again!'}, status = 400)
        
    return JsonResponse({'success': False, 'message' : 'you dont permission to create terminals'})


@require_POST
@csrf_protect
def CreateTerminal(request):
    form = addTerminal(request.POST)
    if form.is_valid:
        form.save()
        return JsonResponse({'success' : True, 'message' : 'Terminal Saved Successfully'}, status = 200)
    return JsonResponse({'success' : False, 'message' : form.errors.as_json(escape_html=True)}, status = 400)

# ADD TERMINAL VIEW PAGE
@staff_member_required(login_url='manager:managerlogin')
def addTerminaLView(request):
    states = State.objects.all()
    return render(request, 'manager/add_terminal.html', {'states' : states})


# STATES VIEW
@staff_member_required(login_url='manager:managerlogin')
def StateView(request):
    if request.method == 'POST':
        form = addState(request.POST)
        if form.is_valid():
            state = form.save(commit=False)
            insate = request.POST.get('name').strip().lower()  # Normalize the state name
            checker = State.objects.filter(name__iexact=insate).first()  # Case-insensitive check
            if checker:
                return JsonResponse({'success': False, 'message': 'State Already Exists'}, status=400)
            state.name = insate.capitalize()  # Store the name capitalized
            state.save()
            return JsonResponse({'success': True, 'message': 'State Saved Successfully'}, status=200)
        errors = form.errors.as_json(escape_html=True)  
        return JsonResponse({'success': False, 'message': errors}, status=400)

    states = State.objects.annotate(
        num_terminals=Count('terminals', distinct=True),
        pickup_vehicles=Count('schedule_pickup_state', distinct=True),
        des_vehicles=Count('schedule_destination_state', distinct=True)
    ).order_by('-id')
    
    return render(request, 'manager/states.html', {'states': states})


@staff_member_required(login_url='/login/')
def StateDetailView(request, statecode):
    checker = State.objects.get(id = statecode)
    if checker:
        terminal = Terminals.objects.filter(state = checker)
        return render(request, 'manager/state-detail.html', {'state' : checker, 'terminals' : terminal})




 #@staff_member_required
class BookingListView(ListView):
    model = Booking
    template_name = "manager/bookings.html"
    context_object_name = 'bookings'
    ordering = '-booking_date'


# SCHEDULES 
def addSchedule(request):
    form = CreateSchedule(request.POST)
    if form.is_valid():
        form.save()
        return JsonResponse({'success' : True, 'message' : 'schedule created successgully'}, status = 200)
    else:
        return JsonResponse({'success' : False, 'message' : form.errors.as_json(escape_html=True)}, status = 400)


# BOOKING DETAILS
def bookingDetailView(request, bookcode):
    try:
        ticket = Booking.objects.get(booking_code = bookcode)
    except Booking.DoesNotExist():
        raise render(request, '404.html', status=404)
    return render(request, 'manager/booking-detail.html', {'ticket' : ticket})











from django.utils.timezone import now
from django.db.models.functions import ExtractMonth
import calendar

def company_analytics(request):
    current_year = now().year
    
    # Aggregate bookings by company for the current year
    bookings = Booking.objects.filter(
        booking_date__year=current_year
    ).values('vehicle__company__name', 'vehicle__company__id').annotate(count=Count('id')).order_by('-count')
    
    # Convert QuerySet to a list of dictionaries
    bookings_list = list(bookings)
    
    # Determine the company with the highest bookings
    top_company = bookings_list[0] if bookings_list else None
    
    # Prepare data for the polar chart
    company_names = [booking['vehicle__company__name'] for booking in bookings_list]
    booking_counts = [booking['count'] for booking in bookings_list]
    
    return render(request, 'manager/company-analytic.html', {
        'company_names': company_names,
        'booking_counts': booking_counts,
        'top_company': top_company
    })