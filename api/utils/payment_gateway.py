from paystackapi.transaction import Transaction
from paystackapi.paystack import Paystack
import requests
from dotenv import load_dotenv
load_dotenv()
import os 
from random import randint
from string import ascii_letters

PAYSTACK_SECRET_KEY = os.getenv('PAYSTACK_SECRET_KEY')

paystack_object = Paystack(PAYSTACK_SECRET_KEY)

def genRandom():
    seq = ''
    for i in range(6):
        index = randint(1, len(ascii_letters)-1)
        seq += ascii_letters[index]
    return seq


def initiate_payment(booking_code : str, amount_to_pay : float,user_email):
    
    amount = float(amount_to_pay) * 100  # Paystack expects the amount in kobo
    
    response = paystack_object.transaction.initialize(
        reference=booking_code,
        amount=amount,
        email=user_email,   
    )

    if response['status']:
        payment_url = response['data']['authorization_url']
        print("Successfully initiated payment")
        print(response)
        access_code =  response['data']['access_code']
        return {"success":True,'payment_url': payment_url,"access_code":access_code ,'access_modified':f'{access_code}-{genRandom()}','amount':amount}
    else:
        print('Error initiating')
        print(response)
        return {'success' : False, 'error': 'Payment initiation failed.'}

def verify_payment(reference):
    response = paystack_object.transaction.verify(reference)
    print(response)
    amount = response['data']['amount']
    id = response['data']['id']
    if response['status'] and response['data']['status'] == 'success':
        # Update the booking status to confirmed
        return {'message': 'Payment made successful.', "reference" : reference, "status":True, 'amount':amount, 'id':id}
    else:
        return {'error': 'Payment verification failed.',"status":False}


# print(verify_payment("T209985684062084"))
# print(verify_payment("BF348394748"))
#print(initiate_payment("BPE-899505", 100000,'kjmorgan@gmail.com'))
# print(genRandom())
# d = '456-iop'
# print(d.split('-'))
# print(d.split('-')[0])