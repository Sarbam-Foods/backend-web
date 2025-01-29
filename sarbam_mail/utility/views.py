from rest_framework import generics
from rest_framework.permissions import AllowAny


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
   permission_classes = (AllowAny,)

class ImageCarouselListAPIView(generics.ListAPIView):
   queryset = ImageCarousel.objects.all()
   serializer_class = ImageCarouselSerializer
   permission_classes = (AllowAny,)


class PromoAdListAPIView(generics.ListAPIView):
   queryset = PromoAd.objects.all()
   serializer_class = PromoAdSerializer
   permission_classes = (AllowAny,)


class AboutListAPIView(generics.ListAPIView):
   queryset = About.objects.all()
   serializer_class = AboutSerializer
   permission_classes = (AllowAny,)
