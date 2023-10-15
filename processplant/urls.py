from django.urls import path
from .views import processPlantViewSet

urlpatterns = [
    path('processplant', processPlantViewSet.as_view({'post':'create'})),
    path('getprocessplant', processPlantViewSet.as_view({'get': 'get'}))
]
