from rest_framework import status, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated

from .serializers import (
    SignUpSerializer,
    FetchUserSerializer,
)
from .models import User

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
    

class FetchUserView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, user_id, *args, **kwargs):
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response(
                {'message': "User doesn't exist!"},
                status= status.HTTP_404_NOT_FOUND
            )
        
        if request.user.id != user.id:
            return Response(
                {'message': "You are not authenticated to view this User!"},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        serializer = FetchUserSerializer(user)

        return Response(serializer.data, status=status.HTTP_200_OK)