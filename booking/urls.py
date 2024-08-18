from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    #path('search-result/', views.inde, name='index'),
    path('dashboard/', views.dashboard_view, name='user_dashboard'),
    path('signup/', views.signup, name='signup'),
    path('login/', views.login_view, name='login'),
    #path('accounts/login/', views.login_view, name='login'),
    path("forgot-password/",views.forgotPassword,name='forgot-password'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.updateProfile, name='profile'),
    path('book/<int:vehicle_id>', views.book, name='book'),
    path('payment/<str:booking_code>/<str:access_code>/<str:amount_to_pay>/', views.makePayment, name='payment'), 
    path('booking_success/<int:booking_id>/', views.booking_success, name='booking_success'),
    path('search_vehicles/', views.search_vehicles, name='search_vehicles'),
    path('search_form/', views.search_form, name='search_form'),
    path('book-now/', views.advanced_search_vehicles, name='advanced_search_vehicles'),
    path("searchHome/", views.searchResult, name="search-from-home")
]
