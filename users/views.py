from rest_framework.views import APIView
from .serializers import UserSerializer, LoginSerializer, EditUserSerializer
from .models import User
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.response import Response
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from rest_framework.permissions import IsAuthenticated
import jwt, datetime
from rest_framework.decorators import api_view, permission_classes
from django.contrib.auth.hashers import check_password
from django.core.mail import EmailMessage, get_connection
from django.conf import settings
from random import randint
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from django.utils import timezone


# Create your views here.
class RegisterView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        data = serializer.data
        user = authenticate(email= serializer.data['email'], password= request.data['password'])
        refresh = RefreshToken.for_user(user)
        return Response({
             "message": "Regisration Successfull",
             'data': data,
             'token': str(refresh.access_token),
             'refresh': str(refresh),
        })
    

class LoginView(APIView):
    def post(self, request):
        # try:
        #     # serializer = LoginSerializer(data=request.data)
        #     # return Response(serializer.is_valid(raise_exception=True))
            
                email = request.data['email']
                password = request.data['password']
                user= User.objects.filter(email=email).first()

                if user is None:
                     return Response({
                        'status': 400,
                        'message': 'User not Founf',
                        'data' : {}
                    }, 404)
                user = authenticate(email= email, password= password)
                if user is None:
                    return Response({
                        'status': 401,
                        'message': 'Incorrect credentials',
                        'data' : {}
                    }, 401)
                refresh = RefreshToken.for_user(user)

                return Response({
                    'status': 200,
                    'message': 'Authenicated Successfully',
                    'token': str(refresh.access_token),
                    'refresh': str(refresh),
                })

class GetUser(APIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = UserSerializer

    def get(self, request, *args, **kwargs):
        serializer = self.serializer_class(request.user)
        if serializer.data['subscription_due_date'] != None and parse_datetime(serializer.data['subscription_due_date']) > timezone.now():
            day = parse_datetime(serializer.data['subscription_due_date']) - timezone.now()
            remaining_days = day.days
        else:
            remaining_days = 0
        return Response({
            'message': 'User Retrieved Successfully',
            'data': {
                'user': serializer.data,
                'remaining_days': remaining_days
                }, 
                }, 200)
    
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def changePassword(request, *args, **kwargs):
    serializer_class = UserSerializer
    user = User.objects.get(id=request.user.id)
    old_password = request.data.get('old_password')
    new_password = request.data.get('new_password')
    confirm_password = request.data.get('confirm_password')
    

    stored_password = user.password
    if (new_password == confirm_password):
        if check_password(old_password, stored_password):
            user.set_password(new_password)
            user.save()
            return Response({
             'message': 'Password Changed Successfully',
            'data': None
        }, 200)
        return Response({
             'message': 'Incorrect Old Password',
            'data': None
        }, 400)
    return Response({
         'message': 'New Password and Confirm Password do not match',
        'data': None
    }, 400)
    
@api_view(['POST'])
def forgotPassword(request):
    receipient_email = request.data.get('email')
    
    
    try:
        # return Response(timezone.now())
        otp = randint(1000, 9000)
        check_user = User.objects.get(email=receipient_email)
        user = User.objects.filter(email=receipient_email).update(reset_otp=otp, otp_request_time=timezone.now())
        # return Response('updated successfully')
        
        with get_connection(  
     host=settings.EMAIL_HOST, 
     port=settings.EMAIL_PORT,  
     username=settings.EMAIL_HOST_USER, 
     password=settings.EMAIL_HOST_PASSWORD, 
     use_tls=settings.EMAIL_USE_TLS
    #  use_ssl=settings.EMAIL_USE_SSL  
       ) as connection:  
           subject = 'Letsplant Password Reset'
           email_from = settings.EMAIL_HOST_USER  
           recipient_list = [request.data.get("email"), ]  
           message = f'Hi, you requested for a password reset, kindly use the below OTP to complete the process, The one time password is valid for 5 minutes, OTP: {otp} if this was not authorized by you kindly ignore'
           EmailMessage(subject, message, email_from, recipient_list, connection=connection).send()  
    
        return Response({ "message": "An instruction on how to reset your password has been sent to your mail "}, status=200)
    except User.DoesNotExist:
        return Response({"message": "Email Does Not Exist"}, status=404)
    
    
@api_view(['POST'])
def resetPassword(request):
    otp = request.data.get('otp')
    email = request.data.get('email')
    new_password = request.data.get('new_password')
    confirm_password = request.data.get('confirm_password')
    
    try:
        user = User.objects.get(email=email)
        stored_otp = user.reset_otp
        
        if(int(stored_otp) == int(otp)):     
            time_difference = timezone.now() - user.otp_request_time
            minutes_difference = round(time_difference.total_seconds() / 60)
            if(minutes_difference > 5):
                return Response({"message": "Expired One time password, kindly request for a new one"}, status=400)
            if (new_password == confirm_password):
                user.set_password(new_password)
                user.save()
                return Response({
                'message': 'Password Changed Successfully',
                'data': None
                }, 200)
            return Response({
            'message': 'New Password and Confirm Password do not match',
            'data': None
        }, 400)

        return Response({"message": "Incorrect One time password"}, status=400)
    
    except User.DoesNotExist:
        return Response({"message": "Email Does Not Exist"}, status=404)

@api_view(['PUT', 'POST'])
@permission_classes([IsAuthenticated])
def editUser(request, *args, **kwargs):
    user = request.user
    serializer = EditUserSerializer(user, data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({
                'message': 'Profile Updated Successfully',
                'data': serializer.data
                }, 200)
        
    return Response({"message":serializer.errors}, status=400)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def deleteUser(request, *args, **kwargs):
    user = request.user
    user.last_login = timezone.now()
    user.save()
    user.delete()
    # refresh_token = request.data.get('token')
    # token = RefreshToken(token)
    # token.blacklist()
    return Response({
                'message': 'Account has been closed successfully Successfully',
                'data': None
                }, 204)
    
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def updateUserPlan(request, *args, **kwargs):
    user = request.user
    selected_plan = request.data['plan'].upper()
    plan = ['FREE','NO-PLAN']
    if selected_plan in plan :
        if(request.data['plan'] == 'FREE' and user.used_free_trial == True):
            return Response({"message": "You have already used your free trial", 'data': None}, status=400)
        elif(request.data['plan'] == 'FREE' and user.used_free_trial == False):
            user.subscription_status = selected_plan
            user.subscription_date = timezone.now()
            user.subscription_due_date = timezone.now() + timezone.timedelta(days=30)
            user.used_free_trial = True
            user.expired = False
            user.save()
            return Response({'message':'You have successfully subscribed to your free trial, which last for 30 days', 'data':None}, status=200)
        else:
            user.subscription_status = selected_plan
            user.expired = True
            user.save()
            return Response({'message':'You have selected the NO Plan option, you won\'t be able to use the functionalities of the app', 'data':None}, status=200)
            
    else:
        return Response({"message": "Invalid plan selected", 'data': None}, status=400)
    

        