from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from .models import Payment, Customer
import requests
from django.conf import settings
from django.http import JsonResponse
from django.http import HttpResponse
from random import randint
from rest_framework.response import Response
import json
from .serializers import PaymentSerializer
from users.models import User
from users.serializers import UserSerializer
from django.utils import timezone


import gocardless_pro



@api_view(['POST'])
@permission_classes([IsAuthenticated])

def makePayment(request):
    user = request.user
    client = gocardless_pro.Client(access_token=settings.GC_TOKEN, environment='live')
    customer, created = Customer.objects.get_or_create(user=user)
    # return Response({'message': 'Customer created successfully', 'data':customer})
    

    try:
        billing_request = client.billing_requests.create(params={
            "payment_request": {
                "amount": "499",
                "currency": "GBP",
                "description": "LetPlant",
                "app_fee": "500",
            },  
            "mandate_request": {
            "scheme": "bacs"
            }
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
        # return JsonResponse(billing_request_data)

        try:
            client = gocardless_pro.Client(access_token=settings.GC_TOKEN, environment='live')
            billingflow = client.billing_request_flows.create(params={
            "redirect_uri": "https://letsplant.com/",
            "exit_uri": "https://letsplant.com/",
            "links": {
                "billing_request": billing_request.id,
                "customer": customer.gocardless_customer_id
            }
            })
            billing_details = {
                "authorised_link": billingflow.authorisation_url,
                "expires_at": billingflow.expires_at,
            }
            user = request.user
            customer = Customer.objects.get(user=user)
            customer.billing_request_id = billingflow.links.billing_request
            customer.save()
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

# Handles the Mandates Events
@api_view(['POST'])
def handleMandateWebhook(request):
    webhook_body = request.body.decode('utf-8')
    webhook_json = json.loads(webhook_body)
    events = webhook_json.get('events', [])
    for event in events:
        if event['resource_type'] == 'mandates' and event['action'] == 'created':
            mandate_id_to_save = event['links']['mandate']
            billing_request_id = event['links']['billing_request']
            for evt in events:
                    if evt['resource_type'] == 'billing_requests' and evt['links'].get('billing_request') == billing_request_id:
                        customer_id = evt['links'].get('customer')
                        try:
                            customer = Customer.objects.get(billing_request_id=billing_request_id)
                            customer.mandate_id = mandate_id_to_save
                            customer.final_customer_id = customer_id
                            customer.save()
                        except Customer.DoesNotExist:
                            return Response(f"Customer with id {customer_id} does not exist")
    
                        client = gocardless_pro.Client(access_token=settings.GC_TOKEN, environment='live')
                        ref = f'LETPSB{randint(1000, 9000)}'
                        subscription = client.subscriptions.create(
                            params={
                                "amount" : 499, # 4.99 GBP in pence    
                                "currency" : "GBP",
                                "interval_unit" : "monthly",
                                "day_of_month" : "1",
                                "links": {
                                    "mandate": customer.mandate_id
                                            # Mandate ID from the last section
                                },
                                "metadata": {
                                    "subscription_number": ref
                                }
                            }, headers={
                                'Idempotency-Key': ref
                        })
                        customer.subscription_id = subscription.id
                        customer.subscription_reference = ref
                        customer.save()
                        return JsonResponse({'status': 'success', "id": subscription.id}, status=200)
        return JsonResponse({'status': 'success, subscribed already'}, status=200)
    return JsonResponse({'error': 'Invalid request method'}, status=405)
    
# @api_view(['POST'])
# def handleCustomerIdWebhook(request):
#     webhook_body = request.body.decode('utf-8')
    
   
    