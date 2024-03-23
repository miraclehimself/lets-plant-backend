from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework import permissions
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.viewsets import ModelViewSet
from django.views.decorators.csrf import csrf_exempt
from rest_framework.response import Response
from .models import processPlant
from .serializers import processPlantSerilizer
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.http import HttpResponse
from django.http import JsonResponse
from PIL import Image
import base64
import cloudinary.uploader
import requests
from django.conf import settings
from geopy.geocoders import Nominatim
# from _future_ import getattr



# from django.conf import settings

# Create your views here.
class processPlantViewSet(ModelViewSet):
    queryset = processPlant.objects.all()
    serializer_class = processPlantSerilizer
    parser_classes = (MultiPartParser, FormParser)
    permission_classes = (permissions.IsAuthenticated,)
    
    @csrf_exempt
    def create(self, request):
        user = request.user
        if user.expired == True:
            return Response({'message': 'Your subscription has expired or You did not have an active subscription. Please subscribe to continue.'}, status=400)

        plant_serializer = processPlantSerilizer(data=request.data)
        plant_serializer.is_valid(raise_exception=True)
        latitude = request.data['latitude']
        longitude = request.data['longitude']
        plant_image = request.data['plant_image']
        image_url = request.FILES['plant_image']
        upload_to_cloud = cloudinary.uploader.upload(image_url)
        # image_path = str(settings.MEDIAROOT) + "/" + plant_image
        # image = request.FILES['plant_image']
       
        
        data = processPlant.objects.create(latitude=latitude, longitude=longitude, plant_image=plant_image, image_url=upload_to_cloud['secure_url'], user=user)
        serializer = processPlantSerilizer(data, many=False)
        impath = f".{serializer.data['plant_image']}"
        # return Response()
        #Make Request to the temperature endpoint
        lat = serializer.data['latitude']
        lon = serializer.data['longitude']
        weather_api_key = "9a1e9c857bbf04988d1d8201eeba3f6e"
        weather_api = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={weather_api_key}"
        
        weather_request = requests.post(weather_api)
        weather_result = weather_request.json()
        temperature = weather_result['main']['temp']
        humidity = weather_result['main']['humidity']
        meta_data = weather_result['main']
    
        #Make Request to the plant identification endpoint
        # with open(impath, 'rb') as image_file:
        #     image_data = base64.b64encode(image_file.read()).decode('utf-8')
        #     api_url = "https://plant.id/api/v3/identification"
        # data = {
        #     'images': image_data
        #     }
        # headers = {
        #     'Api-Key': 'dIF96sc3Cw7bDElhXAPo1e4DSCGS2MoroHydNCNEtIvqYpaMqG'
        #     }
        # response = requests.post(api_url, json=data, headers=headers)
        # return HttpResponse(response)
        
        with open(impath, 'rb') as image_file:
            image_data = image_file.read()
            # image_data = image_file.read()
            PROJECT = 'all'
            API_KEY = '2b109kDMlL07P5egOOKNiarZO'
            api_url = f"https://my-api.plantnet.org/v2/identify/{PROJECT}?api-key={API_KEY}"
        
        data = {
            'organs': ['leaf']
            }
        files = [
            ('images', (impath, image_data))
        ]
    
        response = requests.post(api_url, files=files, data=data)
        resp = response.json()
        if 'statusCode' in resp and resp['statusCode'] == 404 :
            return Response({
                'message': 'This image is not a plant',
                'data': None,
                'status': 'failed',
            },400)
            
        # return JsonResponse(resp, safe=False)
        
        # return HttpResponse(response)
        # return JsonResponse(response, safe=False)
        # is_plant = identification_result['result']['is_plant']['binary']
        # probability = identification_result['result']['is_plant']['probability']
        # if is_plant == False:
        #     return Response({
        #         'message': 'This image is not a plant',
        #         'data': None,
        #         'status': 'failed',
        #     },400)
        
        # if probability < 0.8:
        #     return Response({
        #         'message': 'Unable to identify image',
        #         'data': None,
        #         'status': 'failed',
        #     },400)
        # return JsonResponse(identification_result, safe=False)
        # plant_name = identification_result['result']['classification']['suggestions'][0]['name']
        plant_name = resp['results'][0]['species']['commonNames']
        data = processPlant.objects.filter(id=serializer.data['id']).update(name=plant_name, temperature=temperature, humidity=humidity, meta_data=meta_data)
        updated_data = processPlant.objects.filter(id=serializer.data['id']).order_by('-id')[0]
        serializer = processPlantSerilizer(updated_data, many=False)
        # return JsonResponse(plant_name, safe=False)
        # return Response(response)
            
        return Response({
            'message': 'Image Sent Successfully',
            'data': serializer.data,
            'status': 'success',
        },200)
        
    def get(self, request, *args, **kwargs):
        data = processPlant.objects.filter(user=request.user).all().order_by('-id')
        serializer = processPlantSerilizer(data, many=True)
        return Response(serializer.data, 200)
        
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def gptIntegration(request):
        id = request.data['id']
        user = request.user
        plant_data = processPlant.objects.filter(id=id).first()
        serializer = processPlantSerilizer(plant_data, many=False)
        plant_name = serializer.data['name']
        impath = f".{serializer.data['plant_image']}"
        imageUrl = f"{serializer.data['image_url']}"
        image_file = requests.get(imageUrl).content
        # return Response(impath)
        # with open(impath, 'rb') as image_file:
        image_data = base64.b64encode(image_file).decode('utf-8')
        lat = request.data['latitude']
        lon = request.data['longitude']
        water = request.data['water_frequency']
        sun = request.data['sun_frequency']
        soil = request.data['soil_type']
        symptoms = request.data['symptoms']
        geolocator = Nominatim(user_agent="location_app")
        location = geolocator.reverse((lat, lon), language='en')
        
        # Prepare the prompt for OpenAI
        prompt = f"The watering frequncy of this plant is {water}, while the sun frequency is daily {sun} and the soil type is {soil}, with the symptoms of {symptoms} also Considering the location {location}, and the present condition of this plant, kindly give a recommendation"
        # prompt = f"Considering the location {location}, and the present condition of this plant, kindly give a recommendation"

        openai_api_key = settings.AI_KEY
        headers = {
                'Authorization': f'Bearer {openai_api_key}',
                'Content-Type': 'application/json',
            }
        data = {
                "model": "gpt-4-vision-preview",
                "messages": [
                {
                "role": "user",
                "content": [
                    {
                    "type": "text",
                    # "text": f"{plant_name} Itemize the condition neccesary for this plant to grow and thrive"
                    "text": prompt
                    },
                    {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{image_data}"
                    }
                    }
                ]
                }
            ],
                'max_tokens': 500,
            }
        response = requests.post('https://api.openai.com/v1/chat/completions', json=data, headers=headers)
        # return HttpResponse(response)
        

            # Process and return the response
        identification_result = response.json()
        # return JsonResponse(identification_result, safe=False)
        recommend = identification_result['choices'][0]['message']['content']
        data = processPlant.objects.filter(id=id).update(recommendation=recommend, water_frequency=water, sun_frequency=sun, soil_type=soil, symptoms=symptoms)
        updated_data = processPlant.objects.filter(id=id).order_by('-id')[0]
        serializer = processPlantSerilizer(updated_data, many=False)
        return Response({
            'message': 'Request Successful',
            'data': serializer.data,
            'status': 'success',
        },200)
            # return JsonResponse(identification_result, safe=False)