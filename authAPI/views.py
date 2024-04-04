from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from authAPI.serializers import UserRegistrationSerializer  ,UserSerializer
from authAPI.renderers import UserRenderer
from .models import User
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import get_object_or_404
from django.contrib.auth.hashers import make_password
from django.contrib.auth.hashers import check_password
from django.core.mail import EmailMessage
import random

from django.conf import settings


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)

    return {
        'access_token': str(refresh.access_token),
    }

def send_otp_email(user_email, otp):
    subject = 'Your OTP'
    message = f'Your OTP is: {otp}'
    email = EmailMessage(subject, message, to=[user_email])
    email.send()

class UserRegistrationView(APIView):
  renderer_classes = [UserRenderer]
 
  def post(self,request,format=None):
    serializer = UserRegistrationSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = serializer.save()
    token = get_tokens_for_user(user)
    return Response({'token':token,'msg':'Registration Success'},status=status.HTTP_201_CREATED)

class UserLoginView(APIView):

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        try:
            user = User.object.get(email=email)
        except User.DoesNotExist:
            return Response({'error': 'Invalid email or password'}, status=status.HTTP_401_UNAUTHORIZED)

        if not check_password(password, user.password):
            return Response({'error': 'Invalid email or password'}, status=status.HTTP_401_UNAUTHORIZED)


        token = get_tokens_for_user(user)
        return Response({'token': token}, status=status.HTTP_200_OK)
    

class OTPGenerateView(APIView):
    def post(self, request, format=None):
        email = request.data.get('email')
        print("Emialllll", email)
        # Check if user exists
        try:
            user = User.object.get(email=email)
        except User.DoesNotExist:
            return Response({'msg': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        print("Emialllll 2", user)
        # Generate OTP
        otp = ''.join([str(random.randint(0, 9)) for _ in range(6)])

        # Update user's otp field
        user.otp = otp
        user.save()

        # TODO: Send OTP via SMS or Email (not implemented here)
        send_otp_email(user.email , otp)

        return Response({'msg': 'OTP generated and updated successfully'}, status=status.HTTP_200_OK)
