from django.urls import path
from mail_system import views

urlpatterns = [
   path('order/', views.PlaceOrderView.as_view(), name='place_order'),
]