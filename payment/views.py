from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from .models import Payment
import requests
from django.conf import settings
from django.http import JsonResponse
from django.http import HttpResponse
from rest_framework.response import Response
import json
from .serializers import PaymentSerializer
from users.models import User
from users.serializers import UserSerializer
from django.utils import timezone


import gocardless_pro


# Create your views here.
@api_view(['POST'])
@permission_classes([IsAuthenticated])

def makePayment(request):
    user = request.user
    client = gocardless_pro.Client(access_token=settings.GC_TOKEN, environment='sandbox')
    try:
        billing_request = client.billing_requests.create(params={
            "payment_request": {
                "amount": "9000",
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
            user = request.user
            create_billing = Payment.objects.create(user=user, amount=9000, identity=billing_request.id)
            return JsonResponse(billing_details)
        except gocardless_pro.errors.InvalidApiUsageError as e:
            return HttpResponse(f"Error creating billing request: {e}")    
    except gocardless_pro.errors.InvalidApiUsageError as e:
        return HttpResponse(f"Error creating billing request: {e}")
    
@api_view(['POST'])
def handleWebhook(request):
    webhook_body = request.body.decode('utf-8')
    webhook_json = json.loads(webhook_body)
    event_type = webhook_json['events'][0]['details']['cause']
    if event_type == 'payment_confirmed':
        id = webhook_json['events'][0]['links']['billing_request']
        payment = Payment.objects.get(identity=id)
        user_id = payment.user_id
        user = User.objects.get(id=user_id)
        user.subscription_date = timezone.now() 
        user.subscription_due_date = timezone.now() + timezone.timedelta(days=30)
        user.subscription_status = 'SUBSCRIBED'
        user.expired = False
        user.save()
        user_data = UserSerializer(user, many=False)
        payment.successful = True
        payment.save()
        return Response(user_data.data, 200)
        
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getPayments(request):
    user = request.user
    payment = Payment.objects.filter(user=request.user).all().order_by('-id')
    PaymentHistory = PaymentSerializer(payment, many=True)
    return Response({'message': 'Payment History Returned Successfully','data':PaymentHistory.data, 'status':'success' }, 200)
      
    
   
    