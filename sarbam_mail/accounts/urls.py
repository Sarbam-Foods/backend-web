from django.urls import path

from accounts import views

urlpatterns = [
   path('signup/', views.SignupView.as_view(), name='signup'),
   path('fetch-user-detail/<int:user_id>/', views.FetchUserView.as_view(), name='fetch-user'),
]