from django.urls import path , include
from authAPI.views import  UserRegistrationView,UserLoginView , OTPGenerateView , ChangePassword  ,OTPVerifyView,UserUpdateView,UserDetailView

urlpatterns = [

    path('register/',UserRegistrationView.as_view(),name="register"),
    
    path('login/', UserLoginView.as_view(), name="login"),

    path('otp/', OTPGenerateView.as_view(), name="otp"),

    path('verify/otp/', OTPVerifyView.as_view(), name="otp-verify"),
    
    path('change-password/', ChangePassword.as_view(), name="change-password"),
    
    path('user/update/', UserUpdateView.as_view(), name='user-update'),

    path('user/', UserDetailView.as_view(), name='user-detail'),
]