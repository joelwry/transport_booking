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


def send_email(subject, message, recipient_list):
    send_mail(
        subject,
        message,
        settings.EMAIL_HOST_USER,
        recipient_list,
        fail_silently=False,
    )

def send_booking_confirmation_email(user_email, booking_details):
    subject = 'Booking Confirmation'
    message = f'Your booking has been confirmed. Details: {booking_details}'
    send_email(subject, message, [user_email])

def send_payment_notification_email(user_email, payment_details):
    subject = 'Payment Received'
    message = f'Thank you for your payment. Details: {payment_details}'
    send_email(subject, message, [user_email])
