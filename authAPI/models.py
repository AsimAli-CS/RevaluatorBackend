from django.db import models
from django.contrib.auth.hashers import make_password ,check_password
from django.contrib.auth.models import BaseUserManager
import uuid


# Create your models here.

class UserManager(BaseUserManager):
  def create_user(self, email, first_name , last_name, password):
      """
      Creates and saves a User with the given email, name, tc and password.
      """
      if not email:
          raise ValueError('User must have an email address')
      
      password = make_password(password)

      user = self.model(
          email=self.normalize_email(email),
          first_name = first_name,
          last_name = last_name,
          password=password,
      )
      user.save(using=self._db)
      return user


class User(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)
    image = models.CharField(max_length=300, null=True)
    phone_no = models.CharField(max_length=20, null=True, blank=True)
    company = models.CharField(max_length=100, null=True, blank=True)
    country = models.CharField(max_length=100, null=True, blank=True)
    bio = models.TextField(null=True, blank=True)
    otp = models.CharField(max_length=6, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    object = UserManager()
