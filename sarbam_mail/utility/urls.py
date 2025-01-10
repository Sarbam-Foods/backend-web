from django.urls import path
from utility import views

urlpatterns = [
   path('', views.UtilityListAPIView.as_view(), name='utilities'),
   path('carousel/', views.ImageCarouselListAPIView.as_view(), name='iamge-carousel'),
   path('promo/', views.PromoAdListAPIView.as_view(), name='promo_ads'),
   path('about/', views.AboutListAPIView.as_view(), name='about'),
]