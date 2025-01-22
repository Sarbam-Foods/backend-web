from rest_framework import serializers

from utility.models import Utility, ImageCarousel, PromoAd, About

class UtilitySerializer(serializers.ModelSerializer):
   class Meta:
      model = Utility
      fields = ('show_alert', 'photo', 'title', 'subtitle', 'whatsapp', 'facebook', 'instagram')


class ImageCarouselSerializer(serializers.ModelSerializer):
   class Meta:
      model = ImageCarousel
      fields = ('image1', 'image2', 'image3')


class PromoAdSerializer(serializers.ModelSerializer):
   class Meta:
      model = PromoAd
      fields = ('promo_response',)


class AboutSerializer(serializers.ModelSerializer):
   class Meta:
      model = About
      fields = ('main_text', 'banner_photo', 'banner_photo2', 'text1', 'text2', 'photo1', 'photo2')