from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import hashlib
import requests
from urllib.parse import parse_qs

app = FastAPI()

# PayU merchant credentials
merchant_key = "62Boh5H7"
salt = "3qdfCkKgi1"
base_url = "https://sandboxsecure.payu.in/_payment"

## ... (previous code)

# PayU response handling endpoint
@app.post("/payu-response", response_class=HTMLResponse)
async def payu_response(response_data: dict):
    try:
        # Parse the response data sent by PayU
        response_dict = parse_qs(response_data)

        # Verify the integrity of the response by calculating the hash
        hash_string = (
            f"{merchant_key}|{response_dict['txnid'][0]}|{response_dict['amount'][0]}|{response_dict['productinfo'][0]}|"
            f"{response_dict['firstname'][0]}|{response_dict['email'][0]}||||||||||{salt}"
        )
        calculated_hash = hashlib.sha512(hash_string.encode()).hexdigest()

        # Check if the calculated hash matches the hash sent by PayU
        if calculated_hash != response_dict['hash'][0]:
            raise HTTPException(status_code=400, detail="Hash verification failed")

        # Now you can process the response data and update your database or perform other actions
        # Extract relevant data from response_dict such as txnid, amount, status, etc.
        txnid = response_dict['txnid'][0]
        amount = response_dict['amount'][0]
        status = response_dict['status'][0]

        # Perform actions based on the payment status
        if status == "success":
            # Payment was successful, update your database accordingly
            # You may want to log the payment details or send a confirmation email to the customer
            pass
        elif status == "failure":
            # Payment failed, handle it as needed
            pass
        else:
            # Handle other payment statuses as required
            pass

        # You can customize the HTML response returned to the user as needed
        return HTMLResponse(content="<html><body>Payment response received.</body></html>")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ... (previous code)

class PaymentRequest(BaseModel):
    amount: float
    order_id: str
    email: str


# Endpoint to initiate a PayU payment
@app.post("/initiate-payment")
async def initiate_payment(payment_request: PaymentRequest):
    try:
        # Convert the amount to a string
        amount_str = str(payment_request.amount)

        # Calculate hash to secure the payment request
        hash_string = f"{merchant_key}|{payment_request.order_id}|{amount_str}|{payment_request.email}||||||||||{salt}"
        hash_encoded = hashlib.sha512(hash_string.encode()).hexdigest()

        # Prepare the form data for the payment request
        form_data = {
            "key": merchant_key,
            "txnid": payment_request.order_id,
            "amount": amount_str,
            "productinfo": "YOUR_PRODUCT_INFO",  # Replace with actual product info
            "firstname": "YOUR_CUSTOMER_NAME",  # Replace with customer's first name
            "email": payment_request.email,
            "phone": "YOUR_CUSTOMER_PHONE",  # Replace with customer's phone number
            "surl": "YOUR_SUCCESS_URL",  # Replace with your actual success URL
            "furl": "YOUR_FAILURE_URL",  # Replace with your actual failure URL
            "hash": hash_encoded,
            "service_provider": "payu_paisa",
        }

        # Redirect the user to PayU for payment
        redirect_url = f"{base_url}?{('&'.join([f'{key}={value}' for key, value in form_data.items()]))}"
        return {"redirect_url": redirect_url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
