from django.urls import path

from accounts import views

app_name = 'accounts'

urlpatterns = [
    path('login/', views.LoginAPIView.as_view(), name='login'),
    path('signup/', views.SignupView.as_view(), name='signup'),
   
    path('user/', views.FetchUserView.as_view(), name='fetch-user'),
    path('user/update/', views.UpdateUserAPIView.as_view(), name='update-user'),

    # path('user/address/add/', views.UserAddressCreateAPIView.as_view(), name='add_user_address'),
    # path('user/address/', views.UserAddressAPIView.as_view(), name='user_address'),
    # path('user/address/<int:address_id>/', views.UserAddressUpdateAPIView.as_view(), name='user_address'),

    path('change_password/', views.ChangePasswordAPIView.as_view(), name='change-password'),
    path('forgot_password/', views.ResetPasswordRequestAPIView.as_view(), name='forget-password'),
    path('forgot_password/validate_otp/', views.ValidateOTPView.as_view(), name='validate_otp'),
    path('reset/<str:uid>/<str:token>/', views.ResetPasswordView.as_view(), name='reset-password'),
]