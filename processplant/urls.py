from django.urls import path
from .views import processPlantViewSet
from . import views


urlpatterns = [
    path('processplant', processPlantViewSet.as_view({'post':'create'})),
    path('getprocessplant', processPlantViewSet.as_view({'get': 'get'})),
    path('recommend', views.gptIntegration),
    path('rate', views.ratePlant)

]
