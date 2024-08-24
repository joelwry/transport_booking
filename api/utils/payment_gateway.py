from paystackapi.transaction import Transaction
from paystackapi.paystack import Paystack
import requests
from dotenv import load_dotenv
load_dotenv()
import os 

PAYSTACK_SECRET_KEY = os.getenv('PAYSTACK_SECRET_KEY')

paystack_object = Paystack(PAYSTACK_SECRET_KEY)

def process_payment(booking):
    # Implement logic to generate Paystack payment URL
    payment_url = f"https://paystack.com/pay/{booking.booking_code}"
    return payment_url

def initiate_payment(booking_code : str, amount_to_pay : float,user_email):
    
    print(f'Amount to pay : {amount_to_pay}\nEmail : {user_email}\nBooking Code : {booking_code}')
    amount = float(amount_to_pay) * 100  # Paystack expects the amount in kobo
    
    response = paystack_object.transaction.initialize(
        reference=booking_code,
        amount=amount,
        email=user_email
    )

    if response['status']:
        payment_url = response['data']['authorization_url']
        print("Successfully initiated payment")
        print(response)
        return {"success":True,'payment_url': payment_url,"access_code": response['data']['access_code'] }
    else:
        print('Error initiating')
        print(response)
        return {'success' : False, 'error': f'{response["message"]}. {response["meta"]["nextStep"]}'}

def verify_payment(reference):
    try :
        response = paystack_object.transaction.verify(reference)
        print(response)
        if response['status'] and response['data']['status'] == 'success':
            # Update the booking status to confirmed
            return {'message': 'Payment made successful.', "booking_code" : reference, "status":True,"reference":response['data']['reference'],'amount':response['data']['amount'],'id':response['data']['id']}
        else:
            return {'error': 'Payment verification failed.',"status":False, 'message':response['message']}
    except Exception as e :
        return {'error': str(e),"status":False, 'message':"Error occured verifying payment"}


#print(verify_payment("T209985684062084"))
#print(initiate_payment("BPE-899505", 100000,'kjmorgan@gmail.com'))