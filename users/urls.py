from django.urls import path, include
from .views import RegisterView, LoginView, GetUser

urlpatterns = [
   
    path('register', RegisterView.as_view()),
    path('login', LoginView.as_view()),
    path('user', GetUser.as_view())
]
