from django.core.mail import send_mail
from django.conf import settings
from booking.models import Booking, Payment, Staff

def process_payment(booking, amount, status):
    payment = Payment.objects.create(
        booking=booking,
        amount=amount,
        status=status
    )
    return payment

def send_booking_email(booking):
    subject = 'Booking Confirmation'
    message = f'Your booking is confirmed. Booking ID: {booking.booking_code}'
    recipient_list = [booking.customer.user.email]
    send_mail(subject, message, settings.EMAIL_HOST_USER, recipient_list)

    admin_subject = 'New Booking Alert'
    admin_message = f'A new booking has been made. Booking ID: {booking.booking_code}'
    admin_recipient_list = [admin.user.email for admin in Staff.objects.filter(is_super_admin=True)]
    send_mail(admin_subject, admin_message, settings.EMAIL_HOST_USER, admin_recipient_list)