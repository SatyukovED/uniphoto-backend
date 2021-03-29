from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from django.contrib.auth.models import User
from .models import File
from .validators import validate_file_extension


class UserSerializer(serializers.ModelSerializer):
  email = serializers.EmailField(validators=[UniqueValidator(queryset=User.objects.all(), message=u'1')],
                                 error_messages={'required': u'2', 'blank': u'3'})
  username = serializers.CharField(max_length=150, validators=[UniqueValidator(queryset=User.objects.all(), message=u'1')],
                                   error_messages={'required': u'2', 'blank': u'3'})
  password = serializers.CharField(min_length=8, max_length=100, write_only=True, 
                                   error_messages={'required': u'2', 'blank': u'3', 'min_length': u'4'})

  class Meta:
    model = User
    fields = ('email', 'username', 'password')

  def create(self, validated_data):
    user = User(email=validated_data['email'], username=validated_data['username'])
    user.set_password(validated_data['password'])
    user.save()
    return user

class TrialLicenseCheckSerializer(serializers.Serializer):
  license_duration = serializers.IntegerField(default=30)

class UserFilesSerializer(serializers.ModelSerializer):
  file = serializers.FileField(max_length=None, use_url=True, validators=[validate_file_extension])
  
  class Meta:
    model = File
    fields = ('id', 'file', 'post_date')

class AllFilesSerializer(serializers.ModelSerializer):
  file = serializers.FileField(max_length=None, use_url=True, validators=[validate_file_extension])
  username = serializers.CharField(max_length=150)

  class Meta:
    model = File
    fields = ('id', 'username', 'file', 'post_date')