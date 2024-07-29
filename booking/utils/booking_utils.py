from booking.models import Vehicle, VehicleRoute, State
from django.db.models import Q

def get_vehicles_by_route(start_state_name, destination_state_name):
    start_state = State.objects.get(name=start_state_name)
    destination_state = State.objects.get(name=destination_state_name)
    return Vehicle.objects.filter(
        Q(vehicleroute__state=start_state) & Q(vehicleroute__state=destination_state),
        available=True
    ).distinct()


def get_vehicles_by_router2(start_state_name, destination_state_name):
    start_state = State.objects.get(name=start_state_name)
    destination_state = State.objects.get(name=destination_state_name)
    return Vehicle.objects.filter(
        # vehicle_route__state=start_state,
        #vehicle_route__state=destination_state,
        #vehicle_route_states__in=[start_state, destination_state],
        vehicleroute__state = start_state,
        available=True
    ).distinct()

# not using now 
def get_vehicles_by_router(start_state, destination_state):
    return Vehicle.objects.filter(
        vehicle_route__states__in=[start_state, destination_state]
    ).distinct()

def get_vehicles_by_price(max_price):
    return Vehicle.objects.filter(price__lte=max_price)

def get_vehicles_by_company(company):
    return Vehicle.objects.filter(company=company)

def get_vehicles_by_terminal(terminal):
    return Vehicle.objects.filter(terminal1=terminal) | Vehicle.objects.filter(terminal2=terminal)
