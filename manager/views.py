from django.shortcuts import render, redirect
from booking.models import Vehicle, TransportationCompany, Booking, Terminals, Traveller
from django.contrib.auth import login, authenticate
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.csrf import csrf_protect
from django.http import JsonResponse,HttpRequest



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



# manager index view
@staff_member_required(login_url='manager:managerlogin')
def manageIndexView(request):
    return render(request, "manager/index.html")# manager index view

# add new company
@staff_member_required(login_url='manager:managerlogin')
def AddCompany(request):
    return render(request, "manager/add_company.html")# manager index view


# add new vehicle to lish
@staff_member_required(login_url='manager:managerlogin')
def AddVehicle(request):
    return render(request, "manager/add_vehicle.html")
