from django.shortcuts import render
from rest_framework import permissions
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.viewsets import ModelViewSet
from django.views.decorators.csrf import csrf_exempt
from rest_framework.response import Response
from .models import processPlant
from .serializers import processPlantSerilizer
from django.http import JsonResponse
from PIL import Image
import base64
import requests

# from django.conf import settings

# Create your views here.
class processPlantViewSet(ModelViewSet):
    queryset = processPlant.objects.all()
    serializer_class = processPlantSerilizer
    parser_classes = (MultiPartParser, FormParser)
    permission_classes = (permissions.IsAuthenticated,)
    
    @csrf_exempt
    def create(self, request):
        plant_serializer = processPlantSerilizer(data=request.data)
        plant_serializer.is_valid(raise_exception=True)
        latitude = request.data['latitude']
        longitude = request.data['longitude']
        plant_image = request.data['plant_image']
        
            
        # image_path = str(settings.MEDIAROOT) + "/" + plant_image
        # image = request.FILES['plant_image']
       
        
        user = request.user
        data = processPlant.objects.create(latitude=latitude, longitude=longitude, plant_image=plant_image, user=user)
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
    
        #Make Request to the plant identotfocation endpoint
        with open(impath, 'rb') as image_file:
            image_data = base64.b64encode(image_file.read()).decode('utf-8')
            api_url = "https://plant.id/api/v3/identification"
        data = {
            'images': image_data
            }
        headers = {
            'Api-Key': 'dIF96sc3Cw7bDElhXAPo1e4DSCGS2MoroHydNCNEtIvqYpaMqG'
            }
        response = requests.post(api_url, json=data, headers=headers)
        identification_result = response.json()
        # return JsonResponse(identification_result, safe=False)
        is_plant = identification_result['result']['is_plant']['binary']
        probability = identification_result['result']['is_plant']['probability']
        if is_plant == False:
            return Response({
                'message': 'This image is not a plant',
                'data': None,
                'status': 'failed',
            },400)
        
        if probability < 0.8:
            return Response({
                'message': 'Unable to identify image',
                'data': None,
                'status': 'failed',
            },400)
        # return JsonResponse(identification_result, safe=False)
        plant_name = identification_result['result']['classification']['suggestions'][0]['name']
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
        
        