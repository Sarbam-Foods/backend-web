from rest_framework import generics

from utility.models import (
   Utility,
   ImageCarousel,
   PromoAd,
   About
)
from utility.serializers import (
   UtilitySerializer,
   ImageCarouselSerializer,
   PromoAdSerializer,
   AboutSerializer
)

class UtilityListAPIView(generics.ListAPIView):
   queryset = Utility.objects.all()
   serializer_class = UtilitySerializer


class ImageCarouselListAPIView(generics.ListAPIView):
   queryset = ImageCarousel.objects.all()
   serializer_class = ImageCarouselSerializer


class PromoAdListAPIView(generics.ListAPIView):
   queryset = PromoAd.objects.all()
   serializer_class = PromoAdSerializer


class AboutListAPIView(generics.ListAPIView):
   queryset = About.objects.all()
   serializer_class = AboutSerializer