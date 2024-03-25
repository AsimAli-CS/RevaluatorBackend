from rest_framework import serializers


from authAPI.models import User  # Import your User model


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User  # Specify the User model
        fields = '__all__'  # Or specify the fields you want to include/exclude

class UserRegistrationSerializer(serializers.ModelSerializer):
  class Meta:
    model = User
    fields=['email', 'first_name' , 'last_name', 'password']
    extra_kwargs={
      'password':{'write_only':True}
    }

  def create(self, validate_data):
    return User.object.create_user(**validate_data)
