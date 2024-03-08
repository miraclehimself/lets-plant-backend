from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
import requests
from django.conf import settings
from django.http import JsonResponse
from django.http import HttpResponse
from rest_framework.response import Response
import json

import gocardless_pro


# Create your views here.
@api_view(['POST'])
@permission_classes([IsAuthenticated])

def makePayment(request):
    user = request.user
    client = gocardless_pro.Client(access_token=settings.GC_TOKEN, environment='sandbox')
    # billing_request = client.billing_requests.create(params={
    # "payment_request": {
    #     "description": "First Payment",
    #     "amount": "500",
    #     "currency": "GBP",
    #     "app_fee": "500",
    # }
    # })
    try:
        billing_request = client.billing_requests.create(params={
            "payment_request": {
                "amount": "500",
                "currency": "GBP",
                "description": "letsplantt",
                "app_fee": "500",
            },  
        })
       
        billing_request_data = {
            "id": billing_request.id,
            "created_at": billing_request.created_at,
            "status": billing_request.status,
           "payment_request": {
                "amount": billing_request.payment_request.amount,
                "currency": billing_request.payment_request.currency,
                "description": billing_request.payment_request.description,
                # Include other relevant attributes of PaymentRequest
            },
            # Add other relevant attributes
        }
        try:
            client = gocardless_pro.Client(access_token=settings.GC_TOKEN, environment='sandbox')

            billingflow = client.billing_request_flows.create(params={
            "redirect_uri": "https://letsplant.com/",
            "exit_uri": "https://letsplant.com/",
            "links": {
                "billing_request": billing_request.id
            }
            })
            billing_details = {
                "authorised_link": billingflow.authorisation_url,
                "expires_at": billingflow.expires_at
                
            }
            return JsonResponse(billing_details)
        except gocardless_pro.errors.InvalidApiUsageError as e:
            return HttpResponse(f"Error creating billing request: {e}")    
    except gocardless_pro.errors.InvalidApiUsageError as e:
        return HttpResponse(f"Error creating billing request: {e}")
    