
from booking.forms import AdvancedSearchForm
from booking.models import State, TransportationCompany, Vehicle,Terminals, VehicleSchedule
from datetime import datetime

def indexPageSearchVehiclesSchedule(terminal1_data,terminal2_data,travel_date):
    schedules = None
    if terminal1_data and terminal2_data:
        terminal1_state, terminal1_area = terminal1_data.split('-')
        terminal2_state, terminal2_area = terminal2_data.split('-')

        # Get the terminal objects
        try:
            terminal1 = Terminals.objects.get(state__name=terminal1_state.strip(), area=terminal1_area.strip())
            terminal2 = Terminals.objects.get(state__name=terminal2_state.strip(), area=terminal2_area.strip())
        except Terminals.DoesNotExist:
            terminal1 = None
            terminal2 = None

        if terminal1 and terminal2:
            # Convert travel_date to datetime
            if travel_date:
                travel_date = datetime.strptime(travel_date, '%Y-%m-%d').date()

                # Search for matching vehicle schedules
                schedules = VehicleSchedule.objects.filter(
                    vehicle__terminal1=terminal1,
                    vehicle__terminal2=terminal2,
                    travel_datetime__date=travel_date
                )
            
            else :
                 # Search for matching vehicle schedules
                schedules = VehicleSchedule.objects.filter(
                    vehicle__terminal1=terminal1,
                    vehicle__terminal2=terminal2
                )

        return schedules

    return schedules

def searchForVehicles(request):
    form = AdvancedSearchForm(request.POST or None)
    vehicles = Vehicle.objects.all()
    states = State.objects.all()
    transport_companies = TransportationCompany.objects.all()

    if form.is_valid():
        start_state = form.cleaned_data.get('start_state')
        destination_state = form.cleaned_data.get('destination_state')
        min_price = form.cleaned_data.get('min_price')
        max_price = form.cleaned_data.get('max_price')
        available = form.cleaned_data.get('available')
        company = form.cleaned_data.get('company')

        if start_state and destination_state:
            start_state = State.objects.get(id=int(start_state))
            destination_state = State.objects.get(id=int(destination_state))
            vehicles = vehicles.filter(
                (Q(terminal1__state=start_state) & Q(terminal2__state=destination_state)) | 
                (Q(terminal1__state=destination_state) & Q(terminal2__state=start_state))
            )
        elif start_state:
            start_state = State.objects.get(id=int(start_state))
            vehicles = vehicles.filter(
                Q(terminal1__state=start_state) | Q(terminal2__state=start_state)
            )
        elif destination_state:
            destination_state = State.objects.get(id=int(destination_state))
            vehicles = vehicles.filter(
                Q(terminal1__state=destination_state) | Q(terminal2__state=destination_state)
            )

        if min_price is not None:
            vehicles = vehicles.filter(price__gte=min_price)
        if max_price is not None:
            vehicles = vehicles.filter(price__lte=max_price)
        try:
            print(f'AVAILABILITY : {request.GET.get('availability') }')
            if available and request.GET.get('availability') == "all":
                pass
            elif available or request.GET.get('availability') == None :
                vehicles = vehicles.filter(available=True)
            else :
                vehicles = vehicles.filter(available=False)
        except :
            pass
        if company:
            transport = TransportationCompany.objects.get(id=int(company))
            if transport:
                vehicles = vehicles.filter(company=transport)
    return vehicles