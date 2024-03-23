from django.urls import path
from . import views

urlpatterns = [
    path('payment', views.makePayment),
    path('go-webhook', views.handleWebhook),
    path('get-payments', views.getPayments)
]
