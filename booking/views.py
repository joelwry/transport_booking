from django.shortcuts import render, redirect
from django.contrib.auth import logout, authenticate, login
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from .models import Traveller, Booking, Vehicle, State, TransportationCompany
from .forms import LoginForm, UserRegisterForm, TravellerForm, BookingForm,SignUpForm, AdvancedSearchForm
#from .utils.booking_utils import get_vehicles_by_route
from .utils.payment_utils import process_payment, send_booking_email
from django.utils import timezone
from datetime import timedelta
from django.http import HttpRequest, HttpResponseRedirect
from django.db.models import Q

# will be used to track user login attempt
MAX_ATTEMPTS = 5
LOCKOUT_TIME = 5  # in minutes

# this should be for landing page
def index(request):
    return render(request, 'index.html')

# user dashboard.. user must be authenticated to view this page
@login_required(login_url='/login/')
def dashboard_view(request):
    traveller = Traveller.objects.filter(user = request.user).first()
    tickets = Booking.objects.filter(customer=traveller).all()
    ticket_type_count = {"pending":0,"confirmed":0,"cancelled":0}
    for ticket in tickets:
        if ticket.status == "PENDING":
            ticket.status_color = "pending"
            ticket_type_count['pending'] += 1
            print('pending +1')
        elif ticket.status == "CONFIRMED":
            ticket.status_color = "confirmed"
            ticket_type_count['confirmed'] += 1
        else:
            ticket.status_color = "cancelled"
            ticket_type_count['cancelled'] += 1

    print(tickets)
    print(traveller)
    print(ticket_type_count)
    return render(request, 'booking/user_dashboard.html', {'tickets': tickets, "ticket_analysis":ticket_type_count})

def signup(request):
    if request.method == 'POST':
        print(request.POST)

        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password1'])
            user.save()
            #login(request, user)
            Traveller.objects.create(user=user)
            return redirect('login')
        else:
            form.add_error(None, f"Invalid credentials. Ensure both password are same, password meet minimum requirements and both username and email details are filled appropriately")
    else:
        form = SignUpForm()
    return render(request, 'signup.html', {'form': form})


# we can modify this to only work for Traveller
def signupTraveller(request):
    if request.method == 'POST':
        user_form = UserRegisterForm(request.POST)
        traveller_form = TravellerForm(request.POST)
        if user_form.is_valid() and traveller_form.is_valid():
            user = user_form.save()
            traveller = traveller_form.save(commit=False)
            traveller.user = user
            traveller.save()
            login(request, user)
            return redirect('index')
    else:
        user_form = UserRegisterForm()
        traveller_form = TravellerForm()
    return render(request, 'signup.html', {'user_form': user_form, 'traveller_form': traveller_form})

# ow to check /accounts/login/?next=/dashboard/ if request has next param
def login_view(request: HttpRequest):
    # direct user automatically to dashboard if user is already logged in
    if request.user.is_authenticated:
        return redirect('user_dashboard')

    # Initialize session variables if not already set
    if 'login_attempts' not in request.session:
        request.session['login_attempts'] = 0
    if 'locked_until' not in request.session:
        request.session['locked_until'] = None

    # Check if the user is currently locked out
    if request.session['locked_until']:
        locked_until = timezone.datetime.fromisoformat(request.session['locked_until'])
        if timezone.now() < locked_until:
            form = LoginForm()
            remaining_time = (locked_until - timezone.now()).seconds // 60
            form.add_error(None,f"Too many failed attempts. Try again in {remaining_time} minutes.")
            return render(request, 'login.html', {'form': form, 'error': f"Too many failed attempts. Try again in {remaining_time} minutes."})

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                request.session['login_attempts'] = 0  # Reset attempts after successful login
                request.session['locked_until'] = None  # Reset lockout time
                try : 
                    if request.GET['next'] :
                        return HttpResponseRedirect(request.GET['next'])
                        #return redirect(request.GET['next'])
                        # work on redirect based off next
                except : 
                    print('Not a redirect')
                    pass 
                return redirect('user_dashboard')
            else:
                request.session['login_attempts'] += 1

                if request.session['login_attempts'] >= MAX_ATTEMPTS:
                    lockout_time = timezone.now() + timedelta(minutes=LOCKOUT_TIME)
                    request.session['locked_until'] = lockout_time.isoformat()
                    remaining_time = LOCKOUT_TIME
                    form.add_error(None,f"Too many failed attempts. Try again in {remaining_time} minutes.")
                    return render(request, 'login.html', {'form': form,  })
                else:
                    attempts_left = MAX_ATTEMPTS - request.session['login_attempts']
                    form.add_error(None, f"Invalid credentials. {attempts_left} attempts left.")

    else:
        form = LoginForm()

    return render(request, 'login.html', {'form': form})


# to logout a user, user must have already been logged in b4 he/she can logout
@login_required
def logout_view(request):
    logout(request)
    return redirect('index')

@login_required
def book(request):
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.customer = Traveller.objects.get(user=request.user)
            booking.total_cost = calculate_total_cost(booking)
            booking.save()
            return redirect('payment', booking_id=booking.id)
    else:
        form = BookingForm()
    return render(request, 'booking/booking.html', {'form': form})

@login_required
def payment(request, booking_id):
    booking = Booking.objects.get(id=booking_id)
    if request.method == 'POST':
        amount = request.POST['amount']
        status = request.POST['status']
        payment = process_payment(booking, amount, status)
        if payment.status == 'COMPLETED':
            booking.confirmed = True
            booking.payment_id = payment.id
            booking.save()
            send_booking_email(booking)
            return redirect('booking_success', booking_id=booking.id)
    return render(request, 'booking/payment.html', {'booking': booking})

@login_required
def booking_success(request, booking_id):
    booking = Booking.objects.get(id=booking_id)
    return render(request, 'booking/booking_success.html', {'booking': booking})

# this section shows search result for a traveller trying to find a vehicle that meets his/her requirement
#@login_required
def search_vehicles(request):
    start_state = request.GET.get('start_state')
    destination_state = request.GET.get('destination_state')
    #vehicles = get_vehicles_by_route(start_state, destination_state)
    vehicles = []
    return render(request, 'booking/search_results.html', {'vehicles': vehicles})

# this view will allow travellers to be able to search for vehicles that he/she can book for travelling 
#@login_required
def search_form(request):
    states = State.objects.all()
    return render(request, 'booking/search_form.html', {'states': states})

# this is for advanced search functionality
#@login_required
def advanced_search_vehicles(request):
    form = AdvancedSearchForm(request.GET or None)
    vehicles = Vehicle.objects.all()
    states = State.objects.all()
    transport_companies = TransportationCompany.objects.all()
    
    print(vehicles)

    if form.is_valid():
        print('form sent in ....'.upper())
        start_state = form.cleaned_data.get('start_state')
        destination_state = form.cleaned_data.get('destination_state')
        min_price = form.cleaned_data.get('min_price')
        max_price = form.cleaned_data.get('max_price')
        available = form.cleaned_data.get('available')
        company = form.cleaned_data.get('company')

        print(f'START : {start_state},\nDest : {destination_state},\n Min price : {min_price}\nMax Price :{max_price}\nAvailable: {available},\nCompany : {company}')

        if start_state and destination_state:
            start_state = State.objects.get(id=int(start_state))
            destination_state = State.objects.get(id=int(destination_state))
            vehicle_routes = VehicleRoute.objects.filter(
                (Q(state1=start_state) & Q(state2=destination_state)) | 
                (Q(state1=destination_state) & Q(state2=start_state))
            )
        elif start_state:
            start_state = State.objects.get(id=int(start_state))
            vehicle_routes = VehicleRoute.objects.filter(
                Q(state1=start_state) | Q(state2=start_state)
            )
        elif destination_state:
            destination_state = State.objects.get(id=int(destination_state))
            vehicle_routes = VehicleRoute.objects.filter(
                Q(state1=destination_state) | Q(state2=destination_state)
            )
        else:
            vehicle_routes = VehicleRoute.objects.all()

        vehicles = vehicles.filter(id__in=[route.vehicle.id for route in vehicle_routes])

        if min_price is not None:
            vehicles = vehicles.filter(vehicleroute__price__gte=min_price)
        if max_price is not None:
            vehicles = vehicles.filter(vehicleroute__price__lte=max_price)
        if available:
            vehicles = vehicles.filter(available=True)
        if company:
            transport = TransportationCompany.objects.get(id=int(company))
            if transport:
                vehicles = vehicles.filter(company=transport)

    return render(request, 'booking/book_now.html', { 
        'vehicles': vehicles, 
        'states': states, 
        'transport_companies': transport_companies 
    })

@login_required(login_url='/login/')
def updateProfile(request):
    states = State.objects.all()
    traveller = Traveller.objects.filter(user = request.user).first()
    print(traveller.gender, traveller.state, traveller.phone)
    return render(request, "booking/profile.html", {'states' : states,'traveller':traveller})

def forgotPassword(request):
    return render(request, "forgot_password.html", {})

# Implement the logic to calculate the total cost of booking
def calculate_total_cost(booking):
    return booking.number_of_seats * booking.route.vehicle.price 
