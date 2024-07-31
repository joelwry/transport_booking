from django.contrib import admin
from .models import (
    TransportationCompany, Vehicle, State,
    Traveller, Message, Booking, Payment, Staff,Terminals
)
from django import forms
from django.core.exceptions import ValidationError

@admin.register(TransportationCompany)
class TransportationCompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'address', 'email', 'phone_number')
    search_fields = ('name', 'address', 'email')
    list_filter = ('name',)
    ordering = ('name',)

@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ('plate_number', 'capacity', 'terminal1', 'terminal2', 'available', 'company')
    search_fields = ('plate_number', 'company__name')
    list_filter = ('available', 'company')
    ordering = ('company', 'plate_number')

@admin.register(Terminals)
class TerminalAdmin(admin.ModelAdmin):
    list_display = ('state','area', 'address',)
    search_fields = ('state','area',)
    list_filter = ('state',)

@admin.register(State)
class StateAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    ordering = ('name',)


@admin.register(Traveller)
class TravellerAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone', 'state', 'gender')
    search_fields = ('user__username', 'phone', 'state')
    list_filter = ('gender',)
    ordering = ('user',)

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('type', 'sender', 'message', 'delivered', 'admin_reply')
    search_fields = ('type', 'sender__user__username', 'message')
    list_filter = ('type', 'delivered')
    ordering = ('type', 'sender')
    readonly_fields = ('admin_reply',)

    def get_readonly_fields(self, request, obj=None):
        if request.user.is_staff or request.user.is_superuser:
            return self.readonly_fields
        return self.readonly_fields + ('admin_reply',)

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('booking_code', 'customer', 'status', 'booking_date', 'total_cost', 'confirmed', 'ticket_sent')
    search_fields = ('booking_code', 'start_state__name', 'destination_state__name')
    list_filter = ('status', 'confirmed', 'ticket_sent')
    ordering = ('-booking_date',)

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('booking', 'amount', 'status', 'payment_date')
    search_fields = ('booking__booking_code', 'amount')
    list_filter = ('status',)
    ordering = ('-payment_date',)

@admin.register(Staff)
class StaffAdmin(admin.ModelAdmin):
    list_display = ('user', 'is_super_admin')
    search_fields = ('user__username',)
    list_filter = ('is_super_admin',)
    ordering = ('user',)

