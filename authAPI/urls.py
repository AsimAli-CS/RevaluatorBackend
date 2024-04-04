from django.urls import path , include
from authAPI.views import  UserRegistrationView,UserLoginView , OTPGenerateView  ,OTPVerifyView

urlpatterns = [

    path('register/',UserRegistrationView.as_view(),name="register"),
    
    path('login/', UserLoginView.as_view(), name="login"),

    path('otp/', OTPGenerateView.as_view(), name="otp"),

    path('verify/otp/', OTPVerifyView.as_view(), name="otp-verify"),
    
    path('change-password/', UserLoginView.as_view(), name="login"),

]