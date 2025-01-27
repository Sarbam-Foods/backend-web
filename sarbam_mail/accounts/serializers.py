from rest_framework import serializers
from .models import User, PromoCode, Address
from django.contrib.auth.password_validation import validate_password



class SignUpSerializer(serializers.ModelSerializer):
   password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
   confirm_password = serializers.CharField(write_only=True, required=True)

   class Meta:
      model = User
      fields = ['email', 'name', 'phone_number', 'promocode', 'password', 'confirm_password']
      extra_kwargs = {'password': {'write_only': True}, 'confirm_password': {'write_only': True}}

   def validate(self, data):
      if data['password'] != data['confirm_password']:
         raise serializers.ValidationError({"confirm_password": "The passwords do not match."})
      return data

   def create(self, validated_data):
      validated_data.pop('confirm_password')
      user = User.objects.create_user(**validated_data)
      return user
   

class ChangePasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField(style={'input_type': 'password'}, trim_whitespace=False, write_only=True)
    new_password = serializers.CharField(style={'input_type': 'password'}, trim_whitespace=False, write_only=True)
    confirm_password = serializers.CharField(style={'input_type': 'password'}, trim_whitespace=False, write_only=True)

    def validate_current_password(self, value):
        user = self.context['request'].user

        if not user.check_password(value):
            raise serializers.ValidationError("Current Password is Incorrect!")
        return value

    def validate(self, data):
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError("Passwords do not match.")
        return data
    

class UserActivePromoCodeSerializer(serializers.ModelSerializer):
   class Meta:
      model = PromoCode
      fields = ('id', 'code', 'discount')


class AddressSerializer(serializers.ModelSerializer):
   class Meta:
      model = Address
      fields = ('id', 'user', 'province', 'district', 'municipality', 'location')
   

class FetchUserSerializer(serializers.ModelSerializer):
   promocode = UserActivePromoCodeSerializer(many=True, read_only=True, source='promocode.all')
   address = AddressSerializer(many=True, read_only=True)

   class Meta:
      model = User
      fields = ('id', 'name', 'email', 'phone_number', 'address', 'promocode')



class UserSerializer(serializers.ModelSerializer):   
   address = AddressSerializer(read_only=True, many=True)

   class Meta:
      model = User
      fields = ('id', 'name', 'email', 'phone_number', 'address')


class UpdateUserSerializer(serializers.ModelSerializer):
   class Meta:
      model = User
      fields = ('user', 'name', 'phone_number', 'address')
