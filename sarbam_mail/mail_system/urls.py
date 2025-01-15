from django.urls import path
from mail_system import views

urlpatterns = [
   path('order/', views.PlaceOrderMailView.as_view(), name='place_order'),
]