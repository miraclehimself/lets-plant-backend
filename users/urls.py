from django.urls import path, include
from .views import RegisterView, LoginView, GetUser
from . import views

urlpatterns = [
   
    path('register', RegisterView.as_view()),
    path('login', LoginView.as_view()),
    path('user', GetUser.as_view()),
    path('change-password', views.changePassword),
    path('forgot-password', views.forgotPassword),
    path('reset-password', views.resetPassword),
    path('edit-user', views.editUser),
    path('delete-user', views.deleteUser),
    path('plan', views.updateUserPlan)

]
