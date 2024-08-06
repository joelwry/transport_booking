
def process_payment(booking):
    # Implement logic to generate Paystack payment URL
    payment_url = f"https://paystack.com/pay/{booking.booking_code}"
    return payment_url

def verify_payment(payment):
    # Implement logic to verify payment status with Paystack
    # This is just a mock function for illustration
    payment_status = 'COMPLETED'  # Mock status
    return payment_status
