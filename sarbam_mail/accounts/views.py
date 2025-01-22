import random
from datetime import timedelta

from mail_system.tasks import send_otp_email

from django.urls import reverse
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from django.contrib.auth import authenticate

from rest_framework_simplejwt.tokens import RefreshToken

from rest_framework import status, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated, AllowAny

from .serializers import (
    SignUpSerializer,
    FetchUserSerializer,
    ChangePasswordSerializer,
    UpdateUserSerializer,
    UserSerializer,
)
from .models import User


class LoginAPIView(APIView):
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        if not email and not password:
            return Response(
                {'error': "Email and Password are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = authenticate(request, email=email, password=password)

        if user:
            if not user.is_active:
                return Response(
                    {'error': "Account is not active."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            refresh = RefreshToken.for_user(user)
            user = UserSerializer(user).data

            return Response(
                {
                    'access_token': str(refresh.access_token),
                    'refresh_token': str(refresh),
                    'user': user
                }, 
                status=status.HTTP_200_OK
            )
        else:
            return Response(
                {'error': "Invalid Credentials."},
                status=status.HTTP_400_BAD_REQUEST
            )


class SignupView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = SignUpSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.save()

        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)

        response_data = serializer.data
        response_data['access_token'] = access_token

        return Response(response_data, status=status.HTTP_201_CREATED)


class ChangePasswordAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        serializer = ChangePasswordSerializer(data=request.data, context={'request': request})

        if serializer.is_valid(raise_exception=True):
            user = request.user
            new_password = serializer.validated_data.get('new_password')

            user.set_password(new_password)
            user.save()

            return Response(
                {'message': "Password Changed Successfully!"},
                status = status.HTTP_200_OK
            )
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ResetPasswordRequestAPIView(generics.CreateAPIView):

    def post(self, request):
        email = request.data.get('email')

        try:
            user = User.objects.only('otp', 'otp_expiry').get(email=email)

            user.otp = random.randint(100000, 999999)
            user.otp_expiry = timezone.now() + timedelta(minutes=5)
            user.save()

            reset_url = reverse('accounts:validate_otp')

            send_otp_email.delay(
                email = email,
                otp = user.otp,
                expiry = user.otp_expiry.strftime('%Y-%m-%d %H:%M:%S'),
                name = user.name,
                reset_url = reset_url
            )

            return Response(
                {
                    'message': f'Your OTP has been sent to your mail. This One Time password is valid until {user.otp_expiry}!',
                },
                status= status.HTTP_200_OK
            )
        
        except User.DoesNotExist:
            return Response(
                {'message': 'User with the provided mail doesn\'t exist'},
                status=status.HTTP_400_BAD_REQUEST
            )



class ValidateOTPView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        email = request.data.get('email')
        otp = request.data.get('otp')

        try:
            user = User.objects.get(email=email)

            if user.otp is None and user.otp_expiry is None:
                return Response(
                    {'message': 'No OTP is generated or OTP has expired!'},
                    status = status.HTTP_400_BAD_REQUEST
                )
            
            if timezone.now() > user.otp_expiry:
                user.otp = None
                user.otp_expiry = None
                user.save()
                return Response(
                    {'message': 'OTP has expired!'},
                    status= status.HTTP_400_BAD_REQUEST
                )
            
            if str(user.otp) == str(otp):
                uid = urlsafe_base64_encode(force_bytes(user.pk))
                token = default_token_generator.make_token(user)
                reset_url = f"{request.scheme}://{request.get_host()}/accounts/reset/{uid}/{token}/"
                
                return Response(
                    {
                        'message': 'OTP is valid. Please use the reset URL to change your password.',
                        'reset_url': reset_url
                    },
                    status=status.HTTP_200_OK
                )
            else:
                return Response({'message': 'OTP is not correct.'}, status=status.HTTP_400_BAD_REQUEST)
        
        except User.DoesNotExist:
            return Response({'message': 'No OTP found!'}, status=status.HTTP_400_BAD_REQUEST) 



class ResetPasswordView(APIView):
    def post(self, request, uid, token):
        
        pk = urlsafe_base64_decode(uid).decode()
        try:
            user = User.objects.get(pk=pk)

            if not default_token_generator.check_token(user, token):
                return Response(
                    {
                        'message': 'Token is invalid or Expired!'
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            else:
                new_password = request.data.get('new_password')
                confirm_password = request.data.get('confirm_password')

                if new_password != confirm_password:
                    return Response(
                        {'message': 'Passwords don\'t match!'},
                        status= status.HTTP_400_BAD_REQUEST
                    )
                
                user.set_password(new_password)
                user.otp = None
                user.otp_expiry = None
                user.save()

                return Response(
                    {'message': 'Your Password has been reset successfully!'},
                    status= status.HTTP_200_OK
                )
        
        except ObjectDoesNotExist:
            return Response(
                {'message': 'User does not exist'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        except Exception as e:
            return Response(
                {'message': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )



class FetchUserView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        try:
            user = request.user
        except User.DoesNotExist:
            return Response(
                {'message': "User doesn't exist!"},
                status= status.HTTP_404_NOT_FOUND
            )
                
        serializer = FetchUserSerializer(user)

        return Response(serializer.data, status=status.HTTP_200_OK)
    

class UpdateUserAPIView(generics.GenericAPIView):
    permission_classes = (IsAuthenticated,)

    def patch(self, request, *args, **kwargs):
        try:
            user = request.user
        except User.DoesNotExist:
            return Response(
                {'message': "User doesn't exist!"},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = UpdateUserSerializer(user, data=request.data, partial=True)                
        if serializer.is_valid():
            serializer.save()

            return Response(
                {'message': "User Updated successfully!"},
                status=status.HTTP_200_OK
            )
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )