from rest_framework import serializers
from .models import User
from django.contrib.auth.password_validation import validate_password



class SignUpSerializer(serializers.ModelSerializer):
   password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
   confirm_password = serializers.CharField(write_only=True, required=True)

   class Meta:
      model = User
      fields = ['email', 'name', 'phone_number', 'address', 'promocode', 'password', 'confirm_password']
      extra_kwargs = {'password': {'write_only': True}, 'confirm_password': {'write_only': True}}

   def validate(self, data):
      if data['password'] != data['confirm_password']:
         raise serializers.ValidationError({"confirm_password": "The passwords do not match."})
      return data

   def create(self, validated_data):
      validated_data.pop('confirm_password')
      user = User.objects.create_user(**validated_data)
      return user
   

class FetchUserSerializer(serializers.ModelSerializer):
   class Meta:
      model = User
      fields = ('name', 'email', 'phone_number', 'address', 'promocode')